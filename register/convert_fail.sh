my_list=("P1" "P2" "P15" "P23" "P29" "P30" "P31" "P32" "P46" "P49" "P53" "P56" "P60" "P62" "P63" "P65" "P66" "P67" "P69" "P72" "P73" "P74" "P75" "P77" "P78" "P79" "P80" "P82" "P84" "P88" "P91" "P92" "P93" "P94" "P95" "P96" "P97" "P98" "P99" "P100" "P101" "P109" "P114" "P118" "P119" "P120" "P123" "P124" "P125" "P126" "P127" "P128" "P129" "P130" "P136" "P138" "P139" "P140" "P141" "P142" "P143" "P144" "P145" "P146" "P147" "P148" "P149" "P150" "P151" "P152" "P158" "P159" "P160" "P164" "P165" "P166" "P167" "P168" "P171" "P173" "P174" "P177" "P179" "P182" "P183" "P184" "P185" "P188")
for item in "${my_list[@]}"; do
    # python extract_foreground_region.py "$item"
    # python convert_ets.py "$item"
    python register_valis_all.py "$item"
done