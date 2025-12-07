#!/bin/sh

tstart=60.0
tend=80.0
increment=0.4

threads=8

tcurrent=$tstart

count=0
while (( $(echo "$tcurrent <= $tend" | bc -l) )); do
    tstamp=$(printf "%09.3f" "$tcurrent") #### format may depend on nature run length
    echo "${tstamp}..."
    count=$((count+1))
    python forecast_low_exp.py nature/x4/state_phys_t${tstamp}.nc &> /dev/null &

    if ((count==threads)); then
      wait
      count=0
    fi
    tcurrent=$(echo "$tcurrent + $increment" | bc)
done


