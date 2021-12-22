set nets [get_nets -hierarchical -top_net_of_hierarchical_group]
#  
set outfile [open "data/design.nets" w]
foreach net $nets {
    set pins [get_pins -leaf -of_objects $net]
    puts $outfile "net"
    foreach pin $pins {
        puts -nonewline $outfile "\t"
        puts -nonewline $outfile [get_property "PARENT_CELL" $pin]
        puts -nonewline $outfile " "
        puts $outfile [get_property "REF_PIN_NAME" $pin]
    }
    puts $outfile "endnet"
}
close $outfile