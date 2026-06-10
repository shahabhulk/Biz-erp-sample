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

    function initCustomerAutocomplete(selectEl) {
        const $select = $(selectEl);
        const searchUrl = $select.data('search-url');
        const quickCreateUrl = $select.data('quick-create-url');

        $select.select2({
            theme: 'bootstrap-5',
            placeholder: $select.data('placeholder') || 'Search customer...',
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
                        throw new Error('Could not create customer.');
                    }
                    return response.json();
                })
                .then(function (customer) {
                    const option = new Option(customer.text, customer.id, true, true);
                    $select.append(option).trigger('change');
                })
                .catch(function () {
                    alert('Could not create customer. Use + Full form to add details.');
                });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.customer-autocomplete').forEach(initCustomerAutocomplete);
    });
})();
