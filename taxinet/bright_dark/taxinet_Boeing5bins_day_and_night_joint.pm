dtmc

const N=20;

module taxinet
	scenario: [0..1] init 0;
	// scenario=0 is day
	// scenario=1 is night
	//  state
	cte : [-1..4] init 0;
        // cte=0: on centerline
	// cte=1: left of centerline
        // cte=2: right of centerline
	// cte=3: more left
 	// cte=4: more right
        // cte=-1: off runway ERROR STATE
	he: [-1..2] init 0;
	// he=0: no angle
	// he=1: negative
	// he=2: positive
	//he=-1: ERROR

	// encoding verification results
	v: [0..1] init 1;
	// v=1: certified
	// v=0: not certified

	// estimate of the state from NN
    cte_est: [0..4] init 0;
	he_est: [0..2] init 0; 
	
	//  actions issued by controller
    a: [0 .. 2] init 0; 
        // a=0: go straight
        // a=1: turn left
        // a=2: turn right

  	// program counter
	pc:[0..5] init 0; 
	// 5 is now "sink state"

	// steps
	k:[1..N] init 1;

	//perception

	
	[]  pc=0 -> 1: (v'=1)& (pc'=1);// + 0.1: (v'=0) & (pc'=5);
	

    // NN imperfect perception (Daytime)
[] (scenario=0) & (pc=1)  & (cte=0) & (he=0) ->  0.8218243819266837: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.03751065643648764: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.02557544757033248: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.015345268542199489: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.06308610400682012: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.03665814151747655: (cte_est'=2) & (he_est'=1)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=0) & (he=1) ->  0.015384615384615385: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.8961538461538461: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.007692307692307693: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.026923076923076925: (cte_est'=1) & (he_est'=1)  & (pc'=2) +  0.05384615384615385: (cte_est'=2) & (he_est'=1)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=0) & (he=2) ->  0.009900990099009901: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.0033003300330033004: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.8514851485148515: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.0165016501650165: (cte_est'=1) & (he_est'=2)  & (pc'=2) +  0.026402640264026403: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.0165016501650165: (cte_est'=2) & (he_est'=1)  & (pc'=2) +  0.07590759075907591: (cte_est'=2) & (he_est'=2)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=1) & (he=0) ->  0.07692307692307693: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.06666666666666667: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.005128205128205127: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.811965811965812: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.029059829059829057: (cte_est'=1) & (he_est'=1)  & (pc'=2) +  0.006837606837606838: (cte_est'=1) & (he_est'=2)  & (pc'=2) +  0.003418803418803419: (cte_est'=3) & (he_est'=0)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=1) & (he=1) ->  0.2512820512820513: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.046153846153846156: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.6871794871794872: (cte_est'=1) & (he_est'=1)  & (pc'=2) +  0.005128205128205127: (cte_est'=3) & (he_est'=0)  & (pc'=2) +  0.010256410256410255: (cte_est'=3) & (he_est'=1)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=1) & (he=2) ->  0.031914893617021274: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.026595744680851064: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.0797872340425532: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.03723404255319149: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.7925531914893617: (cte_est'=1) & (he_est'=2)  & (pc'=2) +  0.005319148936170213: (cte_est'=3) & (he_est'=0)  & (pc'=2) +  0.026595744680851064: (cte_est'=3) & (he_est'=2)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=2) & (he=0) ->  0.1421362489486964: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.0008410428931875525: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.7746005046257359: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.05803195962994113: (cte_est'=2) & (he_est'=1)  & (pc'=2) +  0.021867115222876366: (cte_est'=2) & (he_est'=2)  & (pc'=2) +  0.002523128679562658: (cte_est'=4) & (he_est'=0)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=2) & (he=1) ->  0.0040650406504065045: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.08943089430894309: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.008130081300813009: (cte_est'=1) & (he_est'=1)  & (pc'=2) +  0.07723577235772358: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.8170731707317073: (cte_est'=2) & (he_est'=1)  & (pc'=2) +  0.0040650406504065045: (cte_est'=4) & (he_est'=1)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=2) & (he=2) ->  0.027906976744186046: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.10697674418604651: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.013953488372093023: (cte_est'=2) & (he_est'=1)  & (pc'=2) +  0.8418604651162791: (cte_est'=2) & (he_est'=2)  & (pc'=2) +  0.009302325581395349: (cte_est'=4) & (he_est'=2)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=3) & (he=0) ->  0.04: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.05: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.27: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.06: (cte_est'=1) & (he_est'=1)  & (pc'=2) +  0.01: (cte_est'=1) & (he_est'=2)  & (pc'=2) +  0.53: (cte_est'=3) & (he_est'=0)  & (pc'=2) +  0.03: (cte_est'=3) & (he_est'=1)  & (pc'=2) +  0.01: (cte_est'=3) & (he_est'=2)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=3) & (he=1) ->  0.03333333333333333: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.5: (cte_est'=1) & (he_est'=1)  & (pc'=2) +  0.03333333333333333: (cte_est'=3) & (he_est'=0)  & (pc'=2) +  0.43333333333333335: (cte_est'=3) & (he_est'=1)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=3) & (he=2) ->  0.07692307692307693: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.07692307692307693: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.2692307692307692: (cte_est'=1) & (he_est'=2)  & (pc'=2) +  0.5769230769230769: (cte_est'=3) & (he_est'=2)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=4) & (he=0) ->  0.25: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.023809523809523808: (cte_est'=2) & (he_est'=2)  & (pc'=2) +  0.6785714285714286: (cte_est'=4) & (he_est'=0)  & (pc'=2) +  0.017857142857142856: (cte_est'=4) & (he_est'=1)  & (pc'=2) +  0.029761904761904757: (cte_est'=4) & (he_est'=2)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=4) & (he=1) ->  0.07692307692307693: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.3717948717948718: (cte_est'=2) & (he_est'=1)  & (pc'=2) +  0.0641025641025641: (cte_est'=4) & (he_est'=0)  & (pc'=2) +  0.48717948717948717: (cte_est'=4) & (he_est'=1)  & (pc'=2);
[] (scenario=0) & (pc=1)  & (cte=4) & (he=2) ->  0.02857142857142857: (cte_est'=2) & (he_est'=0) & (pc'=2) + 0.14285714285714285: (cte_est'=2) & (he_est'=2) & (pc'=2) + 0.8285714285714286: (cte_est'=4) & (he_est'=2) & (pc'=2);
// NN imperfect perception (NIGHTTIME)
[] (scenario=1) & (pc=1)  & (cte=0) & (he=0) ->  0.3582196697774587: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.4458004307250538: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.010050251256281405: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.0021536252692031586: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.05814788226848529: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.12562814070351758: (cte_est'=2) & (he_est'=1)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=0) & (he=1) ->  0.00196078431372549: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.9274509803921569: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.0058823529411764705: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.00392156862745098: (cte_est'=1) & (he_est'=1)  & (pc'=2) +  0.060784313725490195: (cte_est'=2) & (he_est'=1)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=0) & (he=2) ->  0.42247191011235957: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.05168539325842696: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.18876404494382024: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.20449438202247192: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.10112359550561796: (cte_est'=2) & (he_est'=1)  & (pc'=2) +  0.03146067415730337: (cte_est'=2) & (he_est'=2)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=1) & (he=0) ->  0.18404351767905708: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.6935630099728014: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.0009066183136899365: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.11332728921124206: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.003626473254759746: (cte_est'=1) & (he_est'=1)  & (pc'=2) +  0.004533091568449683: (cte_est'=1) & (he_est'=2)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=1) & (he=1) ->  0.9145569620253164: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.006329113924050634: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.07911392405063292: (cte_est'=1) & (he_est'=1)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=1) & (he=2) ->  0.42810457516339867: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.3006535947712418: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.14052287581699346: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.006535947712418301: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.1111111111111111: (cte_est'=1) & (he_est'=2)  & (pc'=2) +  0.006535947712418301: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.006535947712418301: (cte_est'=2) & (he_est'=1)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=2) & (he=0) ->  0.47286012526096033: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.1315240083507307: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.0010438413361169101: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.2797494780793319: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.10855949895615867: (cte_est'=2) & (he_est'=1)  & (pc'=2) +  0.006263048016701462: (cte_est'=2) & (he_est'=2)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=2) & (he=1) ->  0.011299435028248588: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.5282485875706214: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.005649717514124294: (cte_est'=1) & (he_est'=1)  & (pc'=2) +  0.011299435028248588: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.4435028248587571: (cte_est'=2) & (he_est'=1)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=2) & (he=2) ->  0.3508771929824561: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.011695906432748537: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.07309941520467836: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.2982456140350877: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.03216374269005848: (cte_est'=2) & (he_est'=1)  & (pc'=2) +  0.22807017543859648: (cte_est'=2) & (he_est'=2)  & (pc'=2) +  0.005847953216374269: (cte_est'=4) & (he_est'=2)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=3) & (he=0) ->  0.019230769230769232: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.5448717948717948: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.16666666666666663: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.1858974358974359: (cte_est'=1) & (he_est'=1)  & (pc'=2) +  0.08333333333333331: (cte_est'=3) & (he_est'=0)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=3) & (he=1) ->  0.6363636363636364: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.06818181818181818: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.2727272727272727: (cte_est'=1) & (he_est'=1)  & (pc'=2) +  0.022727272727272728: (cte_est'=3) & (he_est'=1)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=3) & (he=2) ->  0.16666666666666663: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.40476190476190477: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.23809523809523805: (cte_est'=1) & (he_est'=0)  & (pc'=2) +  0.16666666666666663: (cte_est'=1) & (he_est'=2)  & (pc'=2) +  0.023809523809523808: (cte_est'=3) & (he_est'=2)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=4) & (he=0) ->  0.2571428571428571: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.16190476190476188: (cte_est'=0) & (he_est'=2)  & (pc'=2) +  0.42857142857142855: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.004761904761904762: (cte_est'=2) & (he_est'=1)  & (pc'=2) +  0.05238095238095238: (cte_est'=2) & (he_est'=2)  & (pc'=2) +  0.09047619047619047: (cte_est'=4) & (he_est'=0)  & (pc'=2) +  0.004761904761904762: (cte_est'=4) & (he_est'=2)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=4) & (he=1) ->  0.29411764705882354: (cte_est'=0) & (he_est'=0)  & (pc'=2) +  0.20588235294117646: (cte_est'=0) & (he_est'=1)  & (pc'=2) +  0.08823529411764706: (cte_est'=2) & (he_est'=0)  & (pc'=2) +  0.39705882352941174: (cte_est'=2) & (he_est'=1)  & (pc'=2) +  0.014705882352941175: (cte_est'=4) & (he_est'=1)  & (pc'=2);
[] (scenario=1) & (pc=1)  & (cte=4) & (he=2) ->  0.18571428571428573: (cte_est'=0) & (he_est'=0) & (pc'=2) + 0.014285714285714286: (cte_est'=0) & (he_est'=1) & (pc'=2) + 0.21428571428571427: (cte_est'=0) & (he_est'=2) & (pc'=2) + 0.34285714285714285: (cte_est'=2) & (he_est'=0) & (pc'=2) + 0.11428571428571429: (cte_est'=2) & (he_est'=2) & (pc'=2) + 0.04285714285714286: (cte_est'=4) & (he_est'=0) & (pc'=2) + 0.08571428571428571: (cte_est'=4) & (he_est'=2) & (pc'=2);
		
// Quick hack here.
[] (pc=2) -> 1: (pc'=3);
	
    //controller: 
	[] cte_est=0 & he_est=0 & pc=3 -> 1 : (a'=0) & (pc'=4);
	[] cte_est=0 & he_est=1 & pc=3 -> 1 : (a'=2) & (pc'=4);
	[] cte_est=0 & he_est=2 & pc=3 -> 1 : (a'=1) & (pc'=4);
	
	[] (cte_est=1 | cte_est=3) & he_est=0 & pc=3 -> 1 : (a'=2) & (pc'=4);
        [] (cte_est=1 | cte_est=3) & he_est=1 & pc=3 -> 1 : (a'=2) & (pc'=4);
        [] (cte_est=1 | cte_est=3) & he_est=2 & pc=3 -> 1 : (a'=0) & (pc'=4);
	
	[] (cte_est=2 | cte_est=4) & he_est=0 & pc=3 -> 1 : (a'=1) & (pc'=4);
        [] (cte_est=2 | cte_est=4) & he_est=1 & pc=3 -> 1 : (a'=0) & (pc'=4);
        [] (cte_est=2 | cte_est=4) & he_est=2 & pc=3 -> 1 : (a'=1) & (pc'=4);

	//airplane and environment: 
	
	[] he=1 & a=1 & pc=4 & k<N -> 1 : (he'=-1) & (pc'=5);// error
	[] he=2 & a=2 & pc=4 & k<N -> 1 : (he'=-1) & (pc'=5);// error

	[] cte=0 & he=0 & a=0 & pc=4 & k<N -> 1 : (pc'=0) & (k'=k+1);
	[] cte=0 & he=0 & a=1 & pc=4 & k<N -> 1 : (cte'=1) & (he'=1) & (pc'=0) & (k'=k+1);
	[] cte=0 & he=0 & a=2 & pc=4 & k<N -> 1 : (cte'=2) & (he'=2) & (pc'=0) & (k'=k+1);

	[] cte=0 & he=1 & a=0 & pc=4 & k<N -> 1 : (cte'=1) & (pc'=0) & (k'=k+1);
        [] cte=0 & he=1 & a=2 & pc=4 & k<N -> 1 : (he'=0) & (pc'=0) & (k'=k+1);

	[] cte=0 & he=2 & a=0 & pc=4 & k<N -> 1 : (cte'=2) & (pc'=0) & (k'=k+1);
        [] cte=0 & he=2 & a=1 & pc=4 & k<N -> 1 : (he'=0) & (pc'=0) & (k'=k+1);

//left

	[] cte=1 & he=0 & a=0 & pc=4 & k<N -> 1 : (pc'=0) & (k'=k+1);
        [] cte=1 & he=0 & a=1 & pc=4 & k<N -> 1 : (cte'=3) & (he'=1) & (pc'=0) & (k'=k+1);
        [] cte=1 & he=0 & a=2 & pc=4 & k<N -> 1 : (cte'=0) & (he'=2) & (pc'=0) & (k'=k+1);

	[] cte=1 & he=1 & a=0 & pc=4 & k<N -> 1 : (cte'=3) & (pc'=0) & (k'=k+1);
        [] cte=1 & he=1 & a=2 & pc=4 & k<N -> 1 : (he'=0) & (pc'=0) & (k'=k+1);

	[] cte=1 & he=2 & a=0 & pc=4 & k<N -> 1 : (cte'=0) & (pc'=0) & (k'=k+1);
        [] cte=1 & he=2 & a=1 & pc=4 & k<N -> 1 : (he'=0) & (pc'=0) & (k'=k+1);

	[] cte=3 & he=0 & a=0 & pc=4 & k<N -> 1 : (pc'=0) & (k'=k+1);
        [] cte=3 & he=0 & a=1 & pc=4 & k<N -> 1 : (cte'=-1) & (pc'=5); //error
        [] cte=3 & he=0 & a=2 & pc=4 & k<N -> 1 : (cte'=1) & (he'=2) & (pc'=0) & (k'=k+1);

	[] cte=3 & he=1 & a=0 & pc=4 & k<N -> 1 : (cte'=-1) & (pc'=5); //error
        [] cte=3 & he=1 & a=2 & pc=4 & k<N -> 1 : (he'=0) & (pc'=0) & (k'=k+1);

	[] cte=3 & he=2 & a=0 & pc=4 & k<N -> 1 : (cte'=1) & (pc'=0) & (k'=k+1);
        [] cte=3 & he=2 & a=1 & pc=4 & k<N -> 1 : (he'=0) & (pc'=0) & (k'=k+1);

//right

	[] cte=2 & he=0 & a=0 & pc=4 & k<N -> 1 : (pc'=0) & (k'=k+1);
        [] cte=2 & he=0 & a=1 & pc=4 & k<N -> 1 : (cte'=0) & (he'=1) & (pc'=0) & (k'=k+1);
        [] cte=2 & he=0 & a=2 & pc=4 & k<N -> 1 : (cte'=4) & (he'=2) & (pc'=0) & (k'=k+1);

	[] cte=2 & he=1 & a=0 & pc=4 & k<N -> 1 : (cte'=0) & (pc'=0) & (k'=k+1);
        [] cte=2 & he=1 & a=2 & pc=4 & k<N -> 1 : (he'=0) & (pc'=0) & (k'=k+1);

	[] cte=2 & he=2 & a=0 & pc=4 & k<N -> 1 : (cte'=4) & (pc'=0) & (k'=k+1);
        [] cte=2 & he=2 & a=1 & pc=4 & k<N -> 1 : (he'=0) & (pc'=0) & (k'=k+1);

	[] cte=4 & he=0 & a=0 & pc=4 & k<N -> 1 : (pc'=0) & (k'=k+1);
        [] cte=4 & he=0 & a=1 & pc=4 & k<N -> 1 : (cte'=2) & (he'=1) & (pc'=0) & (k'=k+1);
        [] cte=4 & he=0 & a=2 & pc=4 & k<N -> 1 : (cte'=-1) & (pc'=5); //error

	[] cte=4 & he=1 & a=0 & pc=4 & k<N -> 1 : (cte'=2) & (pc'=0) & (k'=k+1);
        [] cte=4 & he=1 & a=2 & pc=4 & k<N -> 1 : (he'=0) & (pc'=0) & (k'=k+1);

	[] cte=4 & he=2 & a=0 & pc=4 & k<N -> 1 : (cte'=-1) & (pc'=5);//error
        [] cte=4 & he=2 & a=1 & pc=4 & k<N -> 1 : (he'=0) & (pc'=0) & (k'=k+1);

endmodule
