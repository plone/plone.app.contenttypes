import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.contenttypes.migration import "
    "BaseClassMigrator, BaseClassMigratorForm, ChangedBaseClasses, "
    "IBaseClassMigratorForm instead.",
    ChangedBaseClasses="plone.app.layout.contenttypes.migration:ChangedBaseClasses",
    IBaseClassMigratorForm="plone.app.layout.contenttypes.migration:IBaseClassMigratorForm",
    BaseClassMigratorForm="plone.app.layout.contenttypes.migration:BaseClassMigratorForm",
    BaseClassMigrator="plone.app.layout.contenttypes.migration:BaseClassMigrator",
)
