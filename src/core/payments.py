"""Stripe payment integration."""
import logging
from decimal import Decimal
from typing import Optional
import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config import get_settings
from src.models.user import User

settings = get_settings()
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = getattr(settings, 'stripe_secret_key', None)


class PaymentManager:
    """Manage payments with Stripe."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment_intent(
        self,
        user_id: str,
        amount: Decimal,
        description: str = "Credit top-up"
    ) -> dict:
        """Create a Stripe payment intent.

        Args:
            user_id: User ID
            amount: Amount in USD
            description: Payment description

        Returns:
            Payment intent data
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        # Create payment intent (amount in cents)
        amount_cents = int(float(amount) * 100)

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                description=description,
                metadata={
                    "user_id": str(user_id),
                    "email": user.email
                }
            )

            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": amount,
                "currency": "usd"
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            raise ValueError(f"Payment failed: {str(e)}")

    async def confirm_payment(
        self,
        payment_intent_id: str
    ) -> bool:
        """Confirm a payment and add credits.

        Args:
            payment_intent_id: Stripe payment intent ID

        Returns:
            Success status
        """
        if not stripe.api_key:
            return False

        try:
            # Retrieve payment intent
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == "succeeded":
                # Get user ID from metadata
                user_id = intent.metadata.get("user_id")
                amount = Decimal(str(intent.amount / 100))

                # Add credits to user
                result = await self.db.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()

                if user:
                    user.credit_balance += amount
                    await self.db.commit()

                    logger.info(f"Added ${amount} credits to user {user_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Payment confirmation error: {str(e)}")
            return False

    async def create_subscription(
        self,
        user_id: str,
        plan: str
    ) -> dict:
        """Create a Stripe subscription.

        Args:
            user_id: User ID
            plan: Subscription plan (starter, pro, enterprise)

        Returns:
            Subscription data
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        # Create or get customer
        if not hasattr(user, 'stripe_customer_id') or not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={"user_id": str(user_id)}
            )
            # Save customer ID (you'd need to add this field to User model)
            # user.stripe_customer_id = customer.id
            # await self.db.commit()
        else:
            customer_id = user.stripe_customer_id

        # Plan price IDs (configure in Stripe Dashboard)
        price_ids = {
            "starter": "price_starter_monthly",
            "pro": "price_pro_monthly",
            "enterprise": "price_enterprise_monthly"
        }

        if plan not in price_ids:
            raise ValueError(f"Invalid plan: {plan}")

        # Create subscription
        try:
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": price_ids[plan]}],
                metadata={
                    "user_id": str(user_id),
                    "plan": plan
                }
            )

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end
            }

        except stripe.error.StripeError as e:
            logger.error(f"Subscription error: {str(e)}")
            raise ValueError(f"Subscription failed: {str(e)}")

    async def cancel_subscription(
        self,
        subscription_id: str
    ) -> bool:
        """Cancel a Stripe subscription.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Success status
        """
        if not stripe.api_key:
            return False

        try:
            stripe.Subscription.delete(subscription_id)
            logger.info(f"Cancelled subscription: {subscription_id}")
            return True

        except stripe.error.StripeError as e:
            logger.error(f"Subscription cancellation error: {str(e)}")
            return False
