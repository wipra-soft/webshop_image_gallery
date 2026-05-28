frappe.ready(() => {
    $('.page_content').on('click', '.wig-thumbnail', (e) => {
        const $img = $(e.currentTarget);
        const link = $img.prop('src');
        const alt = $img.prop('alt') || '';

        const $product_image = $('.product-image');
        $product_image.find('a').prop('href', link);
        $product_image.find('img').prop('src', link);
        $product_image.find('img').prop('alt', alt);

        $('.wig-thumbnail').removeClass('active');
        $img.addClass('active');
    });

    const $zoom_wrapper = $('.wig-zoom-view');

    $('.page_content').on('click', '.website-image', (e) => {
        e.preventDefault();

        const $img = $(e.target);
        const src = $img.prop('src');

        if (!src || !$zoom_wrapper.length) {
            return;
        }

        show_preview(src);
    });

    $zoom_wrapper.on('click', 'button', hide_preview);

    $(document).on('keydown', (e) => {
        if (e.key === 'Escape') {
            hide_preview();
        }
    });

    function show_preview(src) {
        $zoom_wrapper.css('display', 'flex');
        $zoom_wrapper.find('img').remove();
        $zoom_wrapper.append($(`<img src="${src}">`));
    }

    function hide_preview() {
        $zoom_wrapper.find('img').remove();
        $zoom_wrapper.hide();
    }
});

