from django.db import migrations, models
import django.core.validators
import EntreprisesApp.models


class Migration(migrations.Migration):

    dependencies = [
        ('EntreprisesApp', '0002_rename_update_at_entreprise_updated_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entreprise',
            old_name='raison_social',
            new_name='raison_sociale',
        ),
        migrations.RenameField(
            model_name='entreprise',
            old_name='matricul_fiscale',
            new_name='matricule_fiscal',
        ),
        migrations.RenameField(
            model_name='entreprise',
            old_name='adress',
            new_name='adresse',
        ),
        migrations.RenameField(
            model_name='utilisateur',
            old_name='update_at',
            new_name='updated_at',
        ),
        migrations.AlterField(
            model_name='entreprise',
            name='adresse',
            field=models.TextField(validators=[django.core.validators.MinLengthValidator(20, message="L'adresse doit contenir au moins 20 caractères.")]),
        ),
        migrations.AlterField(
            model_name='entreprise',
            name='matricule_fiscal',
            field=models.CharField(max_length=17, unique=True, validators=[EntreprisesApp.models.matricule_fiscal_validator]),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='email',
            field=models.EmailField(max_length=254, unique=True, validators=[EntreprisesApp.models.validate_email]),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='user_id',
            field=models.CharField(blank=True, editable=False, max_length=8, primary_key=True, serialize=False),
        ),
    ]
