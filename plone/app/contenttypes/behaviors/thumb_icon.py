from plone.app.contenttypes import _
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IThumbIconHandling(model.Schema):

    model.fieldset(
        "settings",
        label=_("Settings"),
        fields=[
            "thumb_scale_list",
            "thumb_scale_table",
            "thumb_scale_summary",
            "suppress_icons",
            "suppress_thumbs",
        ],
    )

    thumb_scale_list = schema.TextLine(
        title=_("Override thumb scale for list view"),
        description=_(
            "Enter a valid scale name"
            " (see 'Image Handling' control panel) to override"
            " (e.g. icon, tile, thumb, mini, preview, ... )."
            " Leave empty to use default (see 'Site' control panel)."
        ),
        required=False,
        default="",
    )

    thumb_scale_table = schema.TextLine(
        title=_("Override thumb scale for table view"),
        description=_(
            "Enter a valid scale name"
            " (see 'Image Handling' control panel) to override"
            " (e.g. icon, tile, thumb, mini, preview, ... )."
            " Leave empty to use default (see 'Site' control panel)."
        ),
        required=False,
        default="",
    )

    thumb_scale_summary = schema.TextLine(
        title=_("Override thumb scale for summary view"),
        description=_(
            "Enter a valid scale name"
            " (see 'Image Handling' control panel) to override"
            " (e.g. icon, tile, thumb, mini, preview, ... )."
            " Leave empty to use default (see 'Site' control panel)."
        ),
        required=False,
        default="",
    )

    suppress_icons = schema.Bool(
        title=_("Suppress icons in list, table or summary view"),
        description=_(""),
        required=False,
        default=False,
    )

    suppress_thumbs = schema.Bool(
        title=_("Suppress thumbs in list, table or summary view"),
        required=False,
        default=False,
    )

    directives.omitted(
        "thumb_scale_list",
        "thumb_scale_table",
        "thumb_scale_summary",
        "suppress_icons",
        "suppress_thumbs",
    )
    directives.no_omit(
        IEditForm,
        "thumb_scale_list",
        "thumb_scale_table",
        "thumb_scale_summary",
        "suppress_icons",
        "suppress_thumbs",
    )
    directives.no_omit(
        IAddForm,
        "thumb_scale_list",
        "thumb_scale_table",
        "thumb_scale_summary",
        "suppress_icons",
        "suppress_thumbs",
    )
