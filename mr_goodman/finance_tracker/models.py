from uuid import uuid4

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid4)
    email = models.TextField(unique=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["first_name"]),
            models.Index(fields=["last_name"]),
        ]


class TransactionTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags")
    
    class Meta:
        db_table = "transaction_tags"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "created_by"], name="unique_tag_name_by_user"
            ),
        ]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["name", "created_by_id"]),
            models.Index(fields=["created_at"]),
        ]


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    transaction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    tags = models.ManyToManyField(TransactionTag, related_name="transactions")
    
    class Meta:
        db_table = "transactions"
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=0), name="non_negative_amount"
            ),
            models.CheckConstraint(
                check=models.Q(transaction_date__lte=models.F("created_at")),
                name="transaction_date_not_future",
            ),
            models.UniqueConstraint(
                fields=["amount", "description", "transaction_date", "created_by"],
                name="unique_transaction",
            )
        ]
        indexes = [
            models.Index(fields=["amount"]),
            models.Index(fields=["transaction_date"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["description"]),
        ]


class TransactionReversal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="reversals")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    transaction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reversals")
    
    class Meta:
        db_table = "transaction_reversals"
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=0), name="non_negative_amount"
            ),
            models.CheckConstraint(
                check=models.Q(transaction_date__lte=models.F("created_at")),
                name="transaction_date_not_future",
            ),
            models.UniqueConstraint(
                fields=["transaction", "amount", "description", "transaction_date", "created_by"],
                name="unique_reversal",
            )
        ]
        indexes = [
            models.Index(fields=["amount"]),
            models.Index(fields=["transaction_date"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["description"]),
        ]