# my_list=("P131" "P132" "P133" "P134" "P135" "P137" "P153" "P155" "P156" "P161" "P162" "P163" "P170" "P181" "P189")
# my_list=("P5" "P7" "P8" "P11" "P117" "P129" "P154" "P172" "P178" "P183")
# my_list=("P5" "P7" "P8" "P11" "P117" "P154" "P162" "P172" "P178")
my_list=("P3" "P4" "P5" "P6" "P7" "P8" "P9" "P10" "P11" "P12" "P13" "P14" "P16" "P17" "P18" "P19" "P20" "P21" "P22" "P25" "P27" "P28" "P33" "P34" "P35" "P36" "P37" "P39" "P40" "P42" "P43" "P44" "P45" "P47" "P50" "P52" "P54" "P55" "P58" "P59" "P61" "P64" "P68" "P70" "P71" "P76" "P81" "P83" "P85" "P86" "P87" "P89" "P90" "P103" "P105" "P107" "P108" "P110" "P111" "P112" "P113" "P115" "P116" "P117" "P121" "P122" "P131" "P132" "P133" "P134" "P135" "P137" "P153" "P154" "P155" "P156" "P157" "P161" "P162" "P163" "P170" "P172" "P175" "P176" "P178" "P181" "P189")

for item in "${my_list[@]}"; do
    # python extract_foreground_region.py "$item"
    python convert_ets.py "$item"
    # python register_after_crop.py "$item"
done