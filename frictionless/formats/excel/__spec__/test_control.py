from frictionless import Resource, formats

# General


def test_excel_dialect():
    with Resource("data/table.xlsx") as resource:
        assert isinstance(resource.dialect.get_control("excel"), formats.ExcelControl)

def test_excel_control_to_copy():
    """
    Test that the ExcelControl and all its attributes are correctly copied
    """
    # Make a control with all values changed from the defaults
    control_with_changed_attributes = formats.ExcelControl(
        sheet="non-default",
        fill_merged_cells=True,
        preserve_formatting=True,
        adjust_floating_point_error=True,
        stringified=True
    )

    control_copy = control_with_changed_attributes.to_copy()

    assert control_copy == control_with_changed_attributes
