from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0015_nav_precision_6_decimals'),
    ]

    operations = [
        migrations.AddField(
            model_name='firminvestment',
            name='borrower_name',
            field=models.CharField(blank=True, help_text='Name of the loan borrower', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='firminvestment',
            name='interest_rate',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Interest rate percentage', max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='firminvestment',
            name='interest_rate_period',
            field=models.CharField(
                blank=True,
                choices=[('monthly', 'Per Month'), ('yearly', 'Per Year')],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='firminvestment',
            name='loan_maturity_date',
            field=models.DateField(blank=True, help_text='Date when the loan is due', null=True),
        ),
        # No schema change needed for InvestmentTransaction.amount_type — choices
        # are metadata only. The new 'interest' value fits within max_length=11.
    ]
