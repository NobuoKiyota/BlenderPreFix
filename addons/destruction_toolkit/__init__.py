from . import fracture_core, operators, panels, properties


def register():
    fracture_core.ensure_cell_fracture()
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()

    from .vendor.object_fracture_cell import unregister as _unregister_cell_fracture

    try:
        _unregister_cell_fracture()
    except (RuntimeError, ValueError):
        pass
