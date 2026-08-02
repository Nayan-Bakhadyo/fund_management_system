import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0016_loan_fields_and_interest_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='investmenttransaction',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
