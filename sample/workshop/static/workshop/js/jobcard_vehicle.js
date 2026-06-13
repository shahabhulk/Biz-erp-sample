(function () {
    function initJobCardVehicleForm() {
        const formEl = document.getElementById('jobcard-form');
        const customerSelect = document.getElementById('id_customer');
        const vehicleSelect = document.getElementById('id_vehicle');
        const brandSelect = document.getElementById('id_vehicle_brand');
        const modelSelect = document.getElementById('id_vehicle_model');
        const plateInput = document.getElementById('id_license_plate');
        const chassisInput = document.getElementById('id_chassis_number');

        if (!formEl || !brandSelect || !modelSelect) {
            return;
        }

        const vehicleDetailUrlTemplate = formEl.dataset.vehicleDetailUrl;
        const vehicleSearchUrl = formEl.dataset.vehicleSearchUrl;

        function setBrandModel(brandId, brandName, modelId, modelName) {
            if (window.FleetBrandModel) {
                FleetBrandModel.setSelect2Value($(brandSelect), brandId, brandName);
                FleetBrandModel.setSelect2Value($(modelSelect), modelId, modelName);
            } else {
                if (brandSelect) brandSelect.value = brandId || '';
                if (modelSelect) modelSelect.value = modelId || '';
            }
        }

        function fillFromVehicleDetail(vehicleId) {
            if (!vehicleId || !vehicleDetailUrlTemplate) {
                return;
            }
            const url = vehicleDetailUrlTemplate.replace('{id}', vehicleId);
            fetch(url)
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    setBrandModel(
                        data.brand_id, data.brand_name,
                        data.model_id, data.model_name,
                    );
                    if (plateInput) plateInput.value = data.license_plate || '';
                    if (chassisInput) chassisInput.value = data.chassis_number || '';
                });
        }

        if (vehicleSelect) {
            vehicleSelect.addEventListener('change', function () {
                if (vehicleSelect.value) {
                    fillFromVehicleDetail(vehicleSelect.value);
                }
            });
        }

        if (customerSelect && vehicleSelect && vehicleSearchUrl && window.jQuery) {
            const $vehicle = $(vehicleSelect);
            if ($vehicle.hasClass('select2-hidden-accessible')) {
                $vehicle.select2('destroy');
            }
            $vehicle.select2({
                theme: 'bootstrap-5',
                placeholder: $vehicle.data('placeholder') || 'Search vehicle...',
                allowClear: true,
                width: '100%',
                ajax: {
                    url: vehicleSearchUrl,
                    dataType: 'json',
                    delay: 250,
                    data: function (params) {
                        return {
                            q: params.term || '',
                            customer: customerSelect.value || '',
                        };
                    },
                    processResults: function (data) {
                        return { results: data.results || [] };
                    },
                },
            });
            $vehicle.on('select2:select', function (e) {
                fillFromVehicleDetail(e.params.data.id);
            });
            $vehicle.on('select2:clear', function () {
                if (plateInput) plateInput.value = '';
                if (chassisInput) chassisInput.value = '';
            });

            $(customerSelect).on('change select2:select', function () {
                $vehicle.val(null).trigger('change');
                setBrandModel(null, '', null, '');
                if (plateInput) plateInput.value = '';
                if (chassisInput) chassisInput.value = '';
                updateVehicleFormLink(customerSelect.value);
            });
            updateVehicleFormLink(customerSelect.value);
        }

        function updateVehicleFormLink(customerId) {
            const link = document.getElementById('full-vehicle-form-link');
            if (!link) {
                return;
            }
            const base = link.getAttribute('href').split('?')[0];
            const next = encodeURIComponent(window.location.pathname);
            let href = base + '?next=' + next;
            if (customerId) {
                href += '&customer=' + encodeURIComponent(customerId);
            }
            link.setAttribute('href', href);
        }
    }

    document.addEventListener('DOMContentLoaded', initJobCardVehicleForm);
})();
