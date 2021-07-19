# Generated by Django 2.2.20 on 2021-06-13 23:35
from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations, models
import django.db.models.deletion

from evennia_extensions.character_extensions.constants import (
    RACE_TYPE_CHOICES,
    SMALL_ANIMAL,
    LARGE_ANIMAL,
    PC_RACE,
    SINGLE,
    MARRIED,
    WIDOWED,
    DIVORCED,
)
from server.utils.progress_bar import ProgressBar

aPrefix = "Progress: "


def populate_character_sheets(apps, schema_editor):
    """Populate character sheets with attributes"""
    CharacterSheet = apps.get_model("character_extensions", "CharacterSheet")
    Attribute = apps.get_model("typeclasses", "Attribute")
    sheets = {}
    attr_names = (
        "age",
        "real_age",
        "concept",
        "real_concept",
        "family",
        "vocation",
        "birthday",
        "social_rank",
        "quote",
        "personality",
        "background",
        "obituary",
        "additional_desc",
    )
    integer_attrs = ("age", "real_age", "social_rank")
    qs = Attribute.objects.filter(db_key__in=attr_names)
    if qs:
        total = len(qs)
        num = 0
        print(f"\nConverting {total} attributes to character sheet\n")
        for attr in qs:
            num += 1
            progress = num / total
            try:
                character = attr.objectdb_set.all()[0]
                if character.pk in sheets:
                    sheet = sheets[character.pk]
                else:
                    sheet = CharacterSheet(objectdb=character)
                    sheets[character.pk] = sheet
                if attr.db_key in integer_attrs:
                    value = int(attr.db_value)
                    if value < 0:
                        value = 1
                    if value > 90:
                        value = 90
                else:
                    value = str(attr.db_value)
                setattr(sheet, attr.db_key, value)
                sheet.save()
            except (IndexError, ValueError, TypeError):
                pass
            attr.delete()
            print(ProgressBar(progress, aPrefix), end="\r", flush=True)


def populate_fealty(apps, schema_editor):
    Attribute = apps.get_model("typeclasses", "Attribute")
    Fealty = apps.get_model("dominion", "Fealty")
    fealties = {ob.name.lower(): ob for ob in Fealty.objects.all()}
    qs = Attribute.objects.filter(db_key="fealty")
    if qs:
        total = len(qs)
        num = 0
        print(f"\nConverting {total} fealties")
        for attr in qs:
            num += 1
            progress = num / total
            try:
                character = attr.objectdb_set.all()[0]
                sheet = character.charactersheet
                fealty = fealties[attr.db_value.lower()]
                sheet.fealty = fealty
                sheet.save()
            except (AttributeError, IndexError, KeyError):
                pass
            attr.delete()
            print(ProgressBar(progress, aPrefix), end="\r", flush=True)


def populate_messenger_settings(apps, schema_editor):
    Attribute = apps.get_model("typeclasses", "Attribute")
    MessengerSettings = apps.get_model(
        "character_extensions", "CharacterMessengerSettings"
    )
    ObjectDB = apps.get_model("objects", "ObjectDB")
    messenger_settings = {}
    attr_names = ("discreet_messenger", "custom_messenger", "messenger_draft")
    obj_attrs = ("discreet_messenger", "custom_messenger")
    qs = Attribute.objects.filter(db_key__in=attr_names)
    if qs:
        total = len(qs)
        num = 0
        print(f"\nConverting {total} attributes to messenger settings")
        for attr in qs:
            num += 1
            progress = num / total
            try:
                character = attr.objectdb_set.all()[0]
                if character.pk in messenger_settings:
                    sheet = messenger_settings[character.pk]
                else:
                    sheet = MessengerSettings(objectdb=character)
                    messenger_settings[character.pk] = sheet
                if attr.db_key in obj_attrs:
                    try:
                        value = ObjectDB.objects.get(id=attr.db_value[-1])
                    except (TypeError, ValueError, IndexError, ObjectDB.DoesNotExist):
                        continue
                else:
                    value = str(attr.db_value)
                setattr(sheet, attr.db_key, value)
                sheet.save()
            except (IndexError, ValueError, TypeError):
                pass
            attr.delete()
            print(ProgressBar(progress, aPrefix), end="\r", flush=True)


def populate_titles(apps, schema_editor):
    Attribute = apps.get_model("typeclasses", "Attribute")
    Title = apps.get_model("character_extensions", "CharacterTitle")
    qs = Attribute.objects.filter(db_key="titles")
    if qs:
        total = len(qs)
        num = 0
        print(f"\nConverting {total} titles")
        for attr in qs:
            num += 1
            progress = num / total
            try:
                character = attr.objectdb_set.all()[0]
                for title in attr.db_value:
                    Title.objects.create(character=character, title=title)
            except (IndexError, TypeError, ValueError):
                continue
            attr.delete()
            print(ProgressBar(progress, aPrefix), end="\r", flush=True)


def populate_human_characteristics_and_values(apps, schema_editor):
    Attribute = apps.get_model("typeclasses", "Attribute")
    Race = apps.get_model("character_extensions", "Race")
    Characteristic = apps.get_model("character_extensions", "Characteristic")
    CharacterSheet = apps.get_model("character_extensions", "CharacterSheet")
    CharacteristicValue = apps.get_model("character_extensions", "CharacteristicValue")
    CharacterSheetValue = apps.get_model("character_extensions", "CharacterSheetValue")
    # we'll create humans, but we won't set which values are allowed.
    # staff will curate that list later manually
    human = Race.objects.create(name="human", race_type=PC_RACE)
    hair_color = Characteristic.objects.create(name="hair color")
    eye_color = Characteristic.objects.create(name="eye color")
    gender = Characteristic.objects.create(name="gender")
    height = Characteristic.objects.create(name="height")
    skin_tone = Characteristic.objects.create(name="skin tone")
    # we'll use sheet/characteristic as key to enforce UNIQUE_TOGETHER constraint
    sheet_values = {}
    attr_names = {
        "haircolor": hair_color,
        "eyecolor": eye_color,
        "skintone": skin_tone,
        "gender": gender,
        "height": height,
    }
    tall = CharacteristicValue.objects.create(characteristic=height, value="tall")
    normal_height = CharacteristicValue.objects.create(
        characteristic=height, value="normal height"
    )
    short = CharacteristicValue.objects.create(characteristic=height, value="short")
    female = CharacteristicValue.objects.create(characteristic=gender, value="female")
    male = CharacteristicValue.objects.create(characteristic=gender, value="male")
    fluid = CharacteristicValue.objects.create(characteristic=gender, value="fluid")
    third_gender = CharacteristicValue.objects.create(
        characteristic=gender, value="third gender"
    )

    def get_value_for_height(value):
        """Gets different height character values based on the string value they have"""
        try:
            if value.startswith("4"):
                return short
            if value.startswith("5"):
                return normal_height
            if value.startswith("6"):
                return tall
        except AttributeError:
            pass
        return normal_height

    def get_value_for_gender(value):
        """
        Gets different gender values based on the string value they have. Values
        used here are definitely not meant to be comprehensive - it's just what
        I've seen currently represented in a copy of the database at the time of
        the migration while throwing out garbage values like 'bro'.
        """
        if value.startswith("m") or "boy" in value:
            return male
        if "fluid" in value:
            return fluid
        if "third" in value:
            return third_gender
        return female

    qs = Attribute.objects.filter(db_key__in=attr_names)
    if qs:
        total = len(qs)
        num = 0
        print(f"\nConverting {total} gender, height, eyecolor, etc")
        for attr in qs:
            num += 1
            progress = num / total
            print(ProgressBar(progress, aPrefix), end="\r", flush=True)
            # if the attribute is empty skip it
            if not attr.db_value:
                attr.delete()
                continue
            try:
                character = attr.objectdb_set.all()[0]
                # get or create character sheet associated with the object
                try:
                    sheet = character.charactersheet
                except CharacterSheet.DoesNotExist:
                    sheet = CharacterSheet.objects.create(objectdb=character)
                # get the characteristic for this attribute name
                characteristic = attr_names[attr.db_key]
                # get or create the CharacterSheetValue for the sheet/characteristic pair
                if (sheet.pk, characteristic.pk) in sheet_values:
                    sheet_value = sheet_values[(sheet.pk, characteristic.pk)]
                else:
                    sheet_value = CharacterSheetValue(
                        character_sheet=sheet, characteristic=characteristic
                    )
                    sheet_values[(sheet.pk, characteristic.pk)] = sheet_value
                if attr.db_key == "height":
                    characteristic_value = get_value_for_height(attr.db_value)
                elif attr.db_key == "gender":
                    characteristic_value = get_value_for_gender(attr.db_value.lower())
                else:
                    # get or create the CharacteristicValue for the attr/characteristic pair
                    characteristic_value, _ = CharacteristicValue.objects.get_or_create(
                        value=attr.db_value.lower(), characteristic=characteristic
                    )
                # set the sheet_value to point at that characteristic value
                sheet_value.characteristic_value = characteristic_value
                sheet_value.save()
                try:
                    if character.roster.roster.name in ("Active", "Available"):
                        human.allowed_characteristic_values.add(characteristic_value)
                except AttributeError:
                    pass
            except (IndexError, ValueError, TypeError, AttributeError):
                pass
            attr.delete()


def populate_animal_races_and_breeds(apps, schema_editor):
    """
    We'll create races for PC/NPC races, and then populate the breed characteristic
    based on the value of the species attribute for different types of animal retainers.
    """
    Attribute = apps.get_model("typeclasses", "Attribute")
    Race = apps.get_model("character_extensions", "Race")
    Characteristic = apps.get_model("character_extensions", "Characteristic")
    CharacteristicValue = apps.get_model("character_extensions", "CharacteristicValue")
    CharacterSheet = apps.get_model("character_extensions", "CharacterSheet")
    CharacterSheetValue = apps.get_model("character_extensions", "CharacterSheetValue")
    breed = Characteristic.objects.create(name="breed")
    animal = Race.objects.create(name="animal", race_type=LARGE_ANIMAL)
    small_animal = Race.objects.create(name="small animal", race_type=SMALL_ANIMAL)
    # mapping of sheet to sheet value
    sheet_values = {}
    qs = Attribute.objects.filter(db_key="species")
    if qs:
        total = len(qs)
        num = 0
        print(f"\nConverting {total} species")
        for attr in qs:
            num += 1
            progress = num / total
            print(ProgressBar(progress, aPrefix), end="\r", flush=True)
            # if the attribute is empty skip it
            if not attr.db_value:
                attr.delete()
                continue
            try:
                character = attr.objectdb_set.all()[0]
                npc_type = character.agentob.agent_class.type
                if npc_type == 5:
                    race = animal
                else:
                    race = small_animal
                # get or create character sheet associated with the object
                try:
                    sheet = character.charactersheet
                except CharacterSheet.DoesNotExist:
                    sheet = CharacterSheet.objects.create(objectdb=character)
                # get or create the CharacterSheetValue for the sheet/characteristic pair
                if sheet.pk in sheet_values:
                    sheet_value = sheet_values[sheet.pk]
                else:
                    sheet_value = CharacterSheetValue(
                        character_sheet=sheet, characteristic=breed
                    )
                    sheet_values[sheet.pk] = sheet_value
                # get or create the CharacteristicValue for the attr/characteristic pair
                characteristic_value, _ = CharacteristicValue.objects.get_or_create(
                    value=attr.db_value.lower(), characteristic=breed
                )
                # set the sheet_value to point at that characteristic value
                sheet_value.characteristic_value = characteristic_value
                sheet_value.save()
                # add the characteristic_value as allowed for the race
                race.allowed_characteristic_values.add(characteristic_value)
            except (
                IndexError,
                ValueError,
                TypeError,
                ObjectDoesNotExist,
                AttributeError,
            ):
                pass
            attr.delete()


def populate_held_keys(apps, schema_editor):
    """Migrate attributes chestkeylist and keylist to HeldKey"""
    HeldKey = apps.get_model("character_extensions", "HeldKey")
    Attribute = apps.get_model("typeclasses", "Attribute")
    ObjectDB = apps.get_model("objects", "ObjectDB")
    keys = {}
    id_objectdb_map = {}
    CHEST_KEY, ROOM_KEY = range(2)
    failures = 0

    def process_attribute(attribute, key_type):
        nonlocal failures
        value = attribute.db_value
        try:
            character = attribute.objectdb_set.all()[0]
            # if it's a room, attribute can just be wiped
            if "room" in character.db_typeclass_path:
                attribute.delete()
                return
            for obj_tuple in value:
                obj_id = obj_tuple[-1]
                if obj_id in id_objectdb_map:
                    keyed_object = id_objectdb_map[obj_id]
                else:
                    keyed_object = ObjectDB.objects.get(id=obj_id)
                    id_objectdb_map[obj_id] = keyed_object
                if (character.pk, keyed_object.pk) in keys:
                    continue
                held_key = HeldKey.objects.create(
                    keyed_object=keyed_object, character=character, key_type=key_type
                )
                keys[(character.pk, keyed_object.pk)] = held_key
        except (TypeError, ValueError, IndexError, ObjectDoesNotExist):
            failures += 1
        attribute.delete()

    qs = Attribute.objects.filter(db_key="chestkeylist")
    num = 0
    total = 1
    if qs:
        total = len(qs)
        print(f"\nProcessing {total} chestkeylist attribute")
    for attr in qs:
        num += 1
        progress = num / total
        process_attribute(attr, CHEST_KEY)
        print(ProgressBar(progress, aPrefix), end="\r", flush=True)
    qs = Attribute.objects.filter(db_key="keylist")
    if qs:
        num = 0
        total = len(qs)
        print("\nProcessing keylist attribute")
    for attr in qs:
        num += 1
        progress = num / total
        process_attribute(attr, ROOM_KEY)
        print(ProgressBar(progress, aPrefix), end="\r", flush=True)
    if failures:
        print(f"\nNum failures: {failures}")


def populate_combat_settings(apps, schema_editor):
    CombatSettings = apps.get_model("character_extensions", "CharacterCombatSettings")
    Attribute = apps.get_model("typeclasses", "Attribute")
    ObjectDB = apps.get_model("objects", "ObjectDB")
    settings_map = {}
    attr_names = ("guarding", "xp", "total_xp", "autoattack", "combat_stance")
    qs = Attribute.objects.filter(db_key__in=attr_names)
    failures = 0
    num = 0
    total = len(qs)
    if qs:
        print(f"\nPopulating {total} combat settings")
    for attr in qs:
        num += 1
        progress = num / total
        print(ProgressBar(progress, aPrefix), end="\r", flush=True)
        try:
            character = attr.objectdb_set.all()[0]
            if attr.db_key == "guarding":
                value = ObjectDB.objects.get(id=attr.db_value[-1])
            elif attr.db_key == "autoattack":
                value = bool(attr.db_value)
            elif attr.db_key == "combat_stance":
                value = attr.db_value or ""
            else:
                value = int(attr.db_value or 0)
            settings = settings_map.setdefault(
                character, CombatSettings(objectdb=character)
            )
            setattr(settings, attr.db_key, value)
            settings.save()
        except (IndexError, ObjectDB.DoesNotExist, TypeError, ValueError):
            failures += 1
        attr.delete()
    if failures:
        print(f"\nPopulating settings: {failures} failures")


def populate_marital_status(apps, schema_editor):
    Attribute = apps.get_model("typeclasses", "Attribute")
    qs = Attribute.objects.filter(db_key="marital_status")
    if qs:
        total = len(qs)
        num = 0
        print(f"\nConverting {total} marital_status attributes")
        for attr in qs:
            num += 1
            progress = num / total
            try:
                character = attr.objectdb_set.all()[0]
                sheet = character.charactersheet
                val = attr.db_value.lower()
                if "married" in val:
                    status = MARRIED
                elif "single" in val:
                    status = SINGLE
                elif "divorced" in val or "separated" in val:
                    status = DIVORCED
                elif "widow" in val:
                    status = WIDOWED
                else:
                    status = SINGLE
                sheet.marital_status = status
                sheet.save()
            except (AttributeError, IndexError, ValueError, TypeError):
                pass
            attr.delete()
            print(ProgressBar(progress, aPrefix), end="\r", flush=True)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("dominion", "0003_auto_20210401_0026"),
        (
            "objects",
            "0011_auto_20191025_0831",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Characteristic",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=150, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CharacteristicValue",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.CharField(db_index=True, max_length=80)),
                (
                    "characteristic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="values",
                        to="character_extensions.Characteristic",
                    ),
                ),
            ],
            options={
                "ordering": ("characteristic", "value"),
                "unique_together": {("value", "characteristic")},
            },
        ),
        migrations.CreateModel(
            name="CharacterSheet",
            fields=[
                (
                    "objectdb",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="objects.ObjectDB",
                    ),
                ),
                ("age", models.PositiveSmallIntegerField(default=18)),
                ("real_age", models.PositiveSmallIntegerField(null=True, blank=True)),
                (
                    "marital_status",
                    models.CharField(
                        max_length=30,
                        default="single",
                        choices=[
                            ("single", "Single"),
                            ("married", "Married"),
                            ("widowed", "Widowed"),
                            ("divorced", "Divorced"),
                        ],
                    ),
                ),
                ("concept", models.CharField(blank=True, max_length=255)),
                ("real_concept", models.CharField(blank=True, max_length=255)),
                ("family", models.CharField(blank=True, max_length=255)),
                ("vocation", models.CharField(blank=True, max_length=255)),
                ("birthday", models.CharField(blank=True, max_length=255)),
                ("social_rank", models.PositiveSmallIntegerField(default=10)),
                ("quote", models.TextField(blank=True)),
                ("personality", models.TextField(blank=True)),
                ("background", models.TextField(blank=True)),
                ("obituary", models.TextField(blank=True)),
                ("additional_desc", models.TextField(blank=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Race",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=80, unique=True)),
                ("description", models.TextField(blank=True)),
                (
                    "race_type",
                    models.PositiveSmallIntegerField(
                        choices=RACE_TYPE_CHOICES, default=SMALL_ANIMAL
                    ),
                ),
                (
                    "allowed_characteristic_values",
                    models.ManyToManyField(
                        related_name="allowed_races",
                        to="character_extensions.CharacteristicValue",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="HeldKey",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "key_type",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "chest key"), (1, "room key")], default=0
                    ),
                ),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="held_keys",
                        to="objects.ObjectDB",
                    ),
                ),
                (
                    "keyed_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="distributed_keys",
                        to="objects.ObjectDB",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CharacterTitle",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.TextField(blank=True)),
                (
                    "character",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="character_titles",
                        to="objects.ObjectDB",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CharacterSheetValue",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "character_sheet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="values",
                        to="character_extensions.CharacterSheet",
                    ),
                ),
                (
                    "characteristic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sheet_values",
                        to="character_extensions.Characteristic",
                    ),
                ),
                (
                    "characteristic_value",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sheet_values",
                        to="character_extensions.CharacteristicValue",
                    ),
                ),
            ],
            options={
                "unique_together": {("character_sheet", "characteristic")},
            },
        ),
        migrations.AddField(
            model_name="charactersheet",
            name="characteristics",
            field=models.ManyToManyField(
                related_name="character_sheets",
                through="character_extensions.CharacterSheetValue",
                to="character_extensions.Characteristic",
            ),
        ),
        migrations.AddField(
            model_name="charactersheet",
            name="fealty",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="character_sheets",
                to="dominion.Fealty",
            ),
        ),
        migrations.AddField(
            model_name="charactersheet",
            name="race",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="character_sheets",
                to="character_extensions.Race",
                blank=True,
            ),
        ),
        migrations.CreateModel(
            name="CharacterMessengerSettings",
            fields=[
                (
                    "objectdb",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="objects.ObjectDB",
                    ),
                ),
                ("messenger_draft", models.TextField(blank=True)),
                (
                    "custom_messenger",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="objects.ObjectDB",
                    ),
                ),
                (
                    "discreet_messenger",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="objects.ObjectDB",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "verbose_name_plural": "Character Messenger Settings",
            },
        ),
        migrations.CreateModel(
            name="CharacterCombatSettings",
            fields=[
                (
                    "objectdb",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="objects.ObjectDB",
                    ),
                ),
                ("xp", models.PositiveSmallIntegerField(default=0)),
                ("total_xp", models.PositiveSmallIntegerField(default=0)),
                ("combat_stance", models.CharField(blank=True, max_length=255)),
                ("autoattack", models.BooleanField(default=False)),
                (
                    "guarding",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="guarded_by_sheets",
                        to="objects.ObjectDB",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "verbose_name_plural": "Character Combat Settings",
            },
        ),
        migrations.RunPython(
            populate_character_sheets,
            migrations.RunPython.noop,
            elidable=True,
        ),
        migrations.RunPython(
            populate_held_keys, migrations.RunPython.noop, elidable=True
        ),
        migrations.RunPython(
            populate_combat_settings, migrations.RunPython.noop, elidable=True
        ),
        migrations.RunPython(
            populate_messenger_settings, migrations.RunPython.noop, elidable=True
        ),
        migrations.RunPython(populate_titles, migrations.RunPython.noop, elidable=True),
        migrations.RunPython(
            populate_human_characteristics_and_values,
            migrations.RunPython.noop,
            elidable=True,
        ),
        migrations.RunPython(
            populate_animal_races_and_breeds, migrations.RunPython.noop, elidable=True
        ),
        migrations.RunPython(populate_fealty, migrations.RunPython.noop, elidable=True),
        migrations.RunPython(
            populate_marital_status,
            migrations.RunPython.noop,
            elidable=True,
        ),
    ]