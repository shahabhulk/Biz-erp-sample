(function () {
    function getCookie(name) {
        const cookies = document.cookie ? document.cookie.split(';') : [];
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return null;
    }

    function setSelect2Value($select, id, text) {
        if (!id) {
            $select.val(null).trigger('change');
            return;
        }
        if ($select.find('option[value="' + id + '"]').length === 0) {
            const option = new Option(text, id, true, true);
            $select.append(option);
        } else {
            $select.val(id);
        }
        $select.trigger('change');
    }

    function initBrandAutocomplete(selectEl) {
        const $select = $(selectEl);
        const searchUrl = $select.data('search-url');
        const quickCreateUrl = $select.data('quick-create-url');
        if (!searchUrl || $select.hasClass('select2-hidden-accessible')) {
            return $select;
        }

        $select.select2({
            theme: 'bootstrap-5',
            placeholder: $select.data('placeholder') || 'Search brand...',
            allowClear: true,
            width: '100%',
            ajax: {
                url: searchUrl,
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return { q: params.term || '' };
                },
                processResults: function (data, params) {
                    const results = data.results || [];
                    const term = (params.term || '').trim();
                    if (term && !results.some(function (r) {
                        return r.text.toLowerCase() === term.toLowerCase();
                    })) {
                        results.push({
                            id: 'create:' + term,
                            text: 'Create "' + term + '"',
                        });
                    }
                    return { results: results };
                },
            },
            templateResult: function (data) {
                if (data.id && String(data.id).startsWith('create:')) {
                    return $('<span class="text-primary fw-semibold"></span>').text(data.text);
                }
                return data.text;
            },
        });

        $select.on('select2:select', function (e) {
            const data = e.params.data;
            if (!String(data.id).startsWith('create:')) {
                return;
            }
            const name = String(data.id).slice(7);
            $select.val(null).trigger('change');

            fetch(quickCreateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ name: name }),
            })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error('Could not create brand.');
                    }
                    return response.json();
                })
                .then(function (brand) {
                    setSelect2Value($select, brand.id, brand.text);
                })
                .catch(function () {
                    alert('Could not create brand.');
                });
        });

        return $select;
    }

    function initModelAutocomplete(selectEl) {
        const $select = $(selectEl);
        const searchUrl = $select.data('search-url');
        const quickCreateUrl = $select.data('quick-create-url');
        const brandFieldSelector = $select.data('brand-field') || '#id_vehicle_brand';
        if (!searchUrl || $select.hasClass('select2-hidden-accessible')) {
            return $select;
        }

        function getBrandId() {
            const $brand = $(brandFieldSelector);
            return $brand.val() || '';
        }

        $select.select2({
            theme: 'bootstrap-5',
            placeholder: $select.data('placeholder') || 'Search model...',
            allowClear: true,
            width: '100%',
            ajax: {
                url: searchUrl,
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        q: params.term || '',
                        brand: getBrandId(),
                    };
                },
                processResults: function (data, params) {
                    const results = data.results || [];
                    const term = (params.term || '').trim();
                    if (term && getBrandId() && !results.some(function (r) {
                        return r.text.toLowerCase() === term.toLowerCase();
                    })) {
                        results.push({
                            id: 'create:' + term,
                            text: 'Create "' + term + '"',
                        });
                    }
                    return { results: results };
                },
            },
            templateResult: function (data) {
                if (data.id && String(data.id).startsWith('create:')) {
                    return $('<span class="text-primary fw-semibold"></span>').text(data.text);
                }
                return data.text;
            },
        });

        $select.on('select2:select', function (e) {
            const data = e.params.data;
            if (!String(data.id).startsWith('create:')) {
                return;
            }
            const brandId = getBrandId();
            if (!brandId) {
                alert('Select a car brand first.');
                $select.val(null).trigger('change');
                return;
            }
            const name = String(data.id).slice(7);
            $select.val(null).trigger('change');

            fetch(quickCreateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ name: name, brand_id: brandId }),
            })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error('Could not create model.');
                    }
                    return response.json();
                })
                .then(function (model) {
                    setSelect2Value($select, model.id, model.text);
                })
                .catch(function () {
                    alert('Could not create model.');
                });
        });

        $(brandFieldSelector).on('change select2:select select2:clear', function () {
            $select.val(null).trigger('change');
        });

        return $select;
    }

    window.FleetBrandModel = {
        setSelect2Value: setSelect2Value,
        initBrandAutocomplete: initBrandAutocomplete,
        initModelAutocomplete: initModelAutocomplete,
    };

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.brand-autocomplete').forEach(initBrandAutocomplete);
        document.querySelectorAll('.model-autocomplete').forEach(initModelAutocomplete);
    });
})();
