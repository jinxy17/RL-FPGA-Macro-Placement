set cells [get_cells -hierarchical -filter {IS_PRIMITIVE == 1}]
set outfile [open "data/design.nodes" w]
foreach cell $cells {
    puts -nonewline $outfile $cell
    puts -nonewline $outfile " "
    puts $outfile [get_property "REF_NAME" $cell]
}
close $outfile