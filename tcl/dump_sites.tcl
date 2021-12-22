set sites [get_sites]
set outfile [open "data/design.sites" w]
foreach site $sites {
    # puts -nonewline $outfile $cell
    # puts -nonewline $outfile " "
    puts -nonewline $outfile $site
    puts -nonewline $outfile " "
    puts -nonewline $outfile [get_property "RPM_X" $site]
    puts -nonewline $outfile " "
    puts $outfile [get_property "RPM_Y" $site]
    # puts -nonewline $outfile " "
    # puts $outfile [get_property "SITE_TYPE" $site]
}
close $outfile