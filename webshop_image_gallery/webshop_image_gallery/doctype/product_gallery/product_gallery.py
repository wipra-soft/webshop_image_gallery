# Copyright (c) 2026, WIPRA SOFT Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ProductGallery(Document):
    def validate(self):
        self.validate_gallery_scope()
        self.validate_target_fields()
        self.validate_item_template()
        self.validate_item_variant()
        self.validate_attribute_value_scope()
        self.validate_gallery_images()
        self.set_image_defaults()
        self.validate_primary_image()

    def validate_gallery_scope(self):
        allowed_scopes = {
            "Website Item",
            "Item Template",
            "Item Variant",
            "Attribute Value",
        }

        if not self.gallery_scope:
            frappe.throw(_("Gallery Scope is required."))

        if self.gallery_scope not in allowed_scopes:
            frappe.throw(_("Invalid Gallery Scope: {0}").format(self.gallery_scope))

    def validate_target_fields(self):
        required_by_scope = {
            "Website Item": "website_item",
            "Item Template": "item_template",
            "Item Variant": "item_variant",
            "Attribute Value": "item_template",
        }

        required_field = required_by_scope.get(self.gallery_scope)

        if required_field and not self.get(required_field):
            frappe.throw(
                _("{0} is required for Gallery Scope {1}.").format(
                    frappe.unscrub(required_field),
                    self.gallery_scope,
                )
            )

        if self.gallery_scope != "Website Item" and self.website_item:
            frappe.throw(_("Website Item must only be set when Gallery Scope is Website Item."))

        if self.gallery_scope not in ("Item Template", "Attribute Value") and self.item_template:
            frappe.throw(
                _("Item Template must only be set when Gallery Scope is Item Template or Attribute Value.")
            )

        if self.gallery_scope != "Item Variant" and self.item_variant:
            frappe.throw(_("Item Variant must only be set when Gallery Scope is Item Variant."))

        if self.gallery_scope != "Attribute Value" and (self.attribute or self.attribute_value):
            frappe.throw(
                _("Attribute and Attribute Value must only be set when Gallery Scope is Attribute Value.")
            )

    def validate_item_template(self):
        if self.gallery_scope not in ("Item Template", "Attribute Value") or not self.item_template:
            return

        has_variants = frappe.db.get_value("Item", self.item_template, "has_variants")

        if not has_variants:
            frappe.throw(
                _("Item Template {0} must be an Item with Has Variants enabled.").format(
                    frappe.bold(self.item_template)
                )
            )

    def validate_item_variant(self):
        if self.gallery_scope != "Item Variant" or not self.item_variant:
            return

        variant_of = frappe.db.get_value("Item", self.item_variant, "variant_of")

        if not variant_of:
            frappe.throw(
                _("Item Variant {0} must be an Item with Variant Of set.").format(
                    frappe.bold(self.item_variant)
                )
            )

    def validate_attribute_value_scope(self):
        if self.gallery_scope != "Attribute Value":
            return

        if not self.attribute:
            frappe.throw(_("Attribute is required for Attribute Value gallery."))

        if not self.attribute_value:
            frappe.throw(_("Attribute Value is required for Attribute Value gallery."))

    def validate_gallery_images(self):
        for row in self.images or []:
            if not row.image and not row.get("image_url"):
                frappe.throw(
                    _("Row #{0}: Either Image or Image URL is required.").format(row.idx)
                )

    def set_image_defaults(self):
        for index, row in enumerate(self.images or [], start=1):
            if row.sort_order is None:
                row.sort_order = index

            if row.published is None:
                row.published = 1

    def validate_primary_image(self):
        primary_rows = [row for row in (self.images or []) if row.is_primary]

        if len(primary_rows) > 1:
            frappe.throw(_("Only one image can be marked as Primary."))

        if self.images and not primary_rows:
            first_published = next((row for row in self.images if row.published), None)
            if first_published:
                first_published.is_primary = 1

