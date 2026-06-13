from django.db import transaction

from fleet.models import Vehicle


@transaction.atomic
def resolve_vehicle_for_jobcard(
    *,
    customer,
    vehicle=None,
    brand=None,
    model=None,
    license_plate='',
    chassis_number='',
):
    """
    Find or create a fleet.Vehicle from job card form data (Odoo-style).
    """
    plate = (license_plate or '').strip()
    chassis = (chassis_number or '').strip()

    if vehicle:
        vehicle = Vehicle.objects.select_for_update().get(pk=vehicle.pk, customer=customer)
        updates = {}
        if plate and vehicle.license_plate != plate:
            updates['license_plate'] = plate
        if chassis and vehicle.chassis_number != chassis:
            updates['chassis_number'] = chassis
        if brand and vehicle.brand_id != brand.pk:
            updates['brand'] = brand
        if model and vehicle.model_id != model.pk:
            updates['model'] = model
        if updates:
            for field, value in updates.items():
                setattr(vehicle, field, value)
            vehicle.save(update_fields=list(updates.keys()))
        return vehicle

    if not brand or not model:
        raise ValueError('Car and Model are required for a new vehicle.')

    existing = None
    if plate:
        existing = Vehicle.objects.filter(license_plate__iexact=plate).first()
    if not existing and chassis:
        existing = Vehicle.objects.filter(chassis_number__iexact=chassis).first()

    if not existing:
        return Vehicle.objects.create(
            customer=customer,
            brand=brand,
            model=model,
            license_plate=plate,
            chassis_number=chassis,
        )

    existing.customer = customer
    existing.brand = brand
    existing.model = model
    if plate:
        existing.license_plate = plate
    if chassis:
        existing.chassis_number = chassis
    existing.save()
    return existing
