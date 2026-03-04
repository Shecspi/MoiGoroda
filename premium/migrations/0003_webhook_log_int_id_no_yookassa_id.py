# Generated manually

from django.db import migrations, models
import django.db.models.deletion


def recreate_webhook_log_table(apps, schema_editor):
    """Удалить логи без платежа, пересоздать таблицу с целочисленным PK без yookassa_payment_id."""
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        table = "premium_premiumpaymentwebhooklog"
        # Удаляем строки без платежа (нельзя оставить для NOT NULL)
        cursor.execute(
            f"DELETE FROM {table} WHERE payment_id IS NULL"
        )
        # Создаём новую таблицу с int id и без yookassa_payment_id
        cursor.execute(f"""
            CREATE TABLE {table}_new (
                id SERIAL PRIMARY KEY,
                payment_id UUID NOT NULL REFERENCES premium_premiumpayment(id) ON DELETE CASCADE,
                status VARCHAR(20) NOT NULL,
                raw_payload JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL
            )
        """)
        cursor.execute(f"""
            INSERT INTO {table}_new (payment_id, status, raw_payload, created_at)
            SELECT payment_id, status, raw_payload, created_at
            FROM {table}
        """)
        cursor.execute(f"DROP TABLE {table}")
        cursor.execute(f"ALTER TABLE {table}_new RENAME TO {table}")
        cursor.execute(
            f"ALTER TABLE {table} RENAME CONSTRAINT {table}_new_pkey TO {table}_pkey"
        )
        cursor.execute(
            f"ALTER SEQUENCE {table}_new_id_seq RENAME TO {table}_id_seq"
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('premium', '0002_add_webhook_log'),
    ]

    operations = [
        migrations.RunPython(recreate_webhook_log_table, noop),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='premiumpaymentwebhooklog',
                    name='id',
                ),
                migrations.AddField(
                    model_name='premiumpaymentwebhooklog',
                    name='id',
                    field=models.AutoField(primary_key=True, serialize=False),
                ),
                migrations.RemoveField(
                    model_name='premiumpaymentwebhooklog',
                    name='yookassa_payment_id',
                ),
                migrations.AlterField(
                    model_name='premiumpaymentwebhooklog',
                    name='payment',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='webhook_logs',
                        to='premium.premiumpayment',
                        verbose_name='Платёж',
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
