(function($) {
    $(function() {
        var $isSponsored = $('#id_is_sponsored');
        // Select the rows for sponsor_name and expires_at
        var $sponsoredRows = $('.field-sponsor_name, .field-expires_at');

        function toggleSponsoredFields(checked) {
            if (checked) {
                $sponsoredRows.slideDown();
            } else {
                $sponsoredRows.slideUp();
            }
        }

        // Run on page load
        toggleSponsoredFields($isSponsored.prop('checked'));

        // Run on change
        $isSponsored.change(function() {
            toggleSponsoredFields($(this).prop('checked'));
        });
    });
})(django.jQuery);