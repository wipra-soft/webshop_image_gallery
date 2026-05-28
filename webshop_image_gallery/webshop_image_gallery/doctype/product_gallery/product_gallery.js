// Copyright (c) 2026, WIPRA SOFT Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Product Gallery", {
    refresh(frm) {
        frm.trigger("set_scope_field_visibility");
        frm.trigger("set_scope_field_queries");
        frm.trigger("set_help_text");
    },

    gallery_scope(frm) {
        frm.trigger("set_scope_field_visibility");
        frm.trigger("clear_irrelevant_scope_fields");
    },

    set_scope_field_visibility(frm) {
        const scope = frm.doc.gallery_scope;

        const visibility = {
            website_item: scope === "Website Item",
            item_template: scope === "Item Template" || scope === "Attribute Value",
            item_variant: scope === "Item Variant",
            attribute: scope === "Attribute Value",
            attribute_value: scope === "Attribute Value",
        };

        Object.keys(visibility).forEach((fieldname) => {
            frm.toggle_display(fieldname, visibility[fieldname]);
            frm.toggle_reqd(fieldname, visibility[fieldname]);
        });
    },

    clear_irrelevant_scope_fields(frm) {
        const scope = frm.doc.gallery_scope;

        const fields_to_clear = {
            "Website Item": ["item_template", "item_variant", "attribute", "attribute_value"],
            "Item Template": ["website_item", "item_variant", "attribute", "attribute_value"],
            "Item Variant": ["website_item", "item_template", "attribute", "attribute_value"],
            "Attribute Value": ["website_item", "item_variant"],
        };

        (fields_to_clear[scope] || []).forEach((fieldname) => {
            if (frm.doc[fieldname]) {
                frm.set_value(fieldname, null);
            }
        });
    },

    set_scope_field_queries(frm) {
        frm.set_query("item_template", () => {
            return {
                filters: {
                    has_variants: 1,
                    disabled: 0,
                },
            };
        });

        frm.set_query("item_variant", () => {
            return {
                filters: [
                    ["Item", "variant_of", "!=", ""],
                    ["Item", "disabled", "=", 0],
                ],
            };
        });

        frm.set_query("website_item", () => {
            return {
                filters: {
                    published: 1,
                },
            };
        });
    },

    set_help_text(frm) {
        frm.set_df_property(
            "gallery_scope",
            "description",
            "Choose where this gallery applies. Website Item is most specific. Attribute Value and Item Template are useful for variant-aware fallback galleries."
        );

        frm.set_df_property(
            "images",
            "description",
            "Each row must have either a local image or an external image URL. If both are filled, the local uploaded image is used first."
        );
    },
});

frappe.ui.form.on("Product Gallery Image", {
    image(frm, cdt, cdn) {
        set_child_image_preview_note(frm, cdt, cdn);
    },

    image_url(frm, cdt, cdn) {
        set_child_image_preview_note(frm, cdt, cdn);
    },

    is_primary(frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        if (!row.is_primary) {
            return;
        }

        (frm.doc.images || []).forEach((child) => {
            if (child.name !== row.name && child.is_primary) {
                frappe.model.set_value(child.doctype, child.name, "is_primary", 0);
            }
        });
    },
});

function set_child_image_preview_note(frm, cdt, cdn) {
    const row = locals[cdt][cdn];

    if (!row.image && !row.image_url) {
        frappe.show_alert({
            message: __("Please add either a local image or an external image URL."),
            indicator: "orange",
        });
        return;
    }

    if (row.image && row.image_url) {
        frappe.show_alert({
            message: __("Both image and image URL are set. Local uploaded image will take priority."),
            indicator: "blue",
        });
    }
}
