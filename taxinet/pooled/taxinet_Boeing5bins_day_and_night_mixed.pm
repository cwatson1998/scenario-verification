dtmc

const N=20;

module taxinet
	// There is no scenario, we are mixing Day data with Night data.
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
	

// NN imperfect perception (pooled day and night data)
[] (pc=1)  & (cte=0) & (he=0) ->  0.5701480904130943: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.25915822291504287: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.0171473109898675: (cte_est'=0) & (he_est'=2)  & (pc'=3) +  0.00818394388152767: (cte_est'=1) & (he_est'=0)  & (pc'=3) +  0.06040530007794232: (cte_est'=2) & (he_est'=0)  & (pc'=3) +  0.08495713172252534: (cte_est'=2) & (he_est'=1)  & (pc'=3);
[] (pc=1)  & (cte=0) & (he=1) ->  0.006493506493506494: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.9168831168831169: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.006493506493506494: (cte_est'=1) & (he_est'=0)  & (pc'=3) +  0.011688311688311689: (cte_est'=1) & (he_est'=1)  & (pc'=3) +  0.05844155844155844: (cte_est'=2) & (he_est'=1)  & (pc'=3);
[] (pc=1)  & (cte=0) & (he=2) ->  0.2553475935828877: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.03208556149732621: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.4572192513368984: (cte_est'=0) & (he_est'=2)  & (pc'=3) +  0.0066844919786096255: (cte_est'=1) & (he_est'=2)  & (pc'=3) +  0.1323529411764706: (cte_est'=2) & (he_est'=0)  & (pc'=3) +  0.06684491978609626: (cte_est'=2) & (he_est'=1)  & (pc'=3) +  0.04946524064171123: (cte_est'=2) & (he_est'=2)  & (pc'=3);
[] (pc=1)  & (cte=1) & (he=0) ->  0.14691943127962084: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.476303317535545: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.002369668246445498: (cte_est'=0) & (he_est'=2)  & (pc'=3) +  0.35545023696682465: (cte_est'=1) & (he_est'=0)  & (pc'=3) +  0.012440758293838863: (cte_est'=1) & (he_est'=1)  & (pc'=3) +  0.00533175355450237: (cte_est'=1) & (he_est'=2)  & (pc'=3) +  0.001184834123222749: (cte_est'=3) & (he_est'=0)  & (pc'=3);
[] (pc=1)  & (cte=1) & (he=1) ->  0.6614481409001957: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.021526418786692758: (cte_est'=1) & (he_est'=0)  & (pc'=3) +  0.3111545988258317: (cte_est'=1) & (he_est'=1)  & (pc'=3) +  0.0019569471624266144: (cte_est'=3) & (he_est'=0)  & (pc'=3) +  0.003913894324853229: (cte_est'=3) & (he_est'=1)  & (pc'=3);
[] (pc=1)  & (cte=1) & (he=2) ->  0.2773279352226721: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.19635627530364372: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.11740890688259109: (cte_est'=0) & (he_est'=2)  & (pc'=3) +  0.018218623481781375: (cte_est'=1) & (he_est'=0)  & (pc'=3) +  0.37044534412955465: (cte_est'=1) & (he_est'=2)  & (pc'=3) +  0.004048582995951417: (cte_est'=2) & (he_est'=0)  & (pc'=3) +  0.004048582995951417: (cte_est'=2) & (he_est'=1)  & (pc'=3) +  0.0020242914979757085: (cte_est'=3) & (he_est'=0)  & (pc'=3) +  0.010121457489878543: (cte_est'=3) & (he_est'=2)  & (pc'=3);
[] (pc=1)  & (cte=2) & (he=0) ->  0.2897065673032138: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.05868653935724266: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.0009315323707498836: (cte_est'=0) & (he_est'=2)  & (pc'=3) +  0.5537959944108057: (cte_est'=2) & (he_est'=0)  & (pc'=3) +  0.08057755006986493: (cte_est'=2) & (he_est'=1)  & (pc'=3) +  0.014904517931998137: (cte_est'=2) & (he_est'=2)  & (pc'=3) +  0.0013972985561248254: (cte_est'=4) & (he_est'=0)  & (pc'=3);
[] (pc=1)  & (cte=2) & (he=1) ->  0.008333333333333333: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.34833333333333333: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.006666666666666667: (cte_est'=1) & (he_est'=1)  & (pc'=3) +  0.03833333333333333: (cte_est'=2) & (he_est'=0)  & (pc'=3) +  0.5966666666666667: (cte_est'=2) & (he_est'=1)  & (pc'=3) +  0.0016666666666666668: (cte_est'=4) & (he_est'=1)  & (pc'=3);
[] (pc=1)  & (cte=2) & (he=2) ->  0.21543985637342908: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.00718132854578097: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.05565529622980251: (cte_est'=0) & (he_est'=2)  & (pc'=3) +  0.2244165170556553: (cte_est'=2) & (he_est'=0)  & (pc'=3) +  0.025134649910233394: (cte_est'=2) & (he_est'=1)  & (pc'=3) +  0.4649910233393178: (cte_est'=2) & (he_est'=2)  & (pc'=3) +  0.00718132854578097: (cte_est'=4) & (he_est'=2)  & (pc'=3);
[] (pc=1)  & (cte=3) & (he=0) ->  0.02734375: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.3515625: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.20703125: (cte_est'=1) & (he_est'=0)  & (pc'=3) +  0.13671875: (cte_est'=1) & (he_est'=1)  & (pc'=3) +  0.00390625: (cte_est'=1) & (he_est'=2)  & (pc'=3) +  0.2578125: (cte_est'=3) & (he_est'=0)  & (pc'=3) +  0.01171875: (cte_est'=3) & (he_est'=1)  & (pc'=3) +  0.00390625: (cte_est'=3) & (he_est'=2)  & (pc'=3);
[] (pc=1)  & (cte=3) & (he=1) ->  0.3918918918918919: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.04054054054054054: (cte_est'=1) & (he_est'=0)  & (pc'=3) +  0.36486486486486486: (cte_est'=1) & (he_est'=1)  & (pc'=3) +  0.013513513513513514: (cte_est'=3) & (he_est'=0)  & (pc'=3) +  0.1891891891891892: (cte_est'=3) & (he_est'=1)  & (pc'=3);
[] (pc=1)  & (cte=3) & (he=2) ->  0.10294117647058823: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.27941176470588236: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.17647058823529413: (cte_est'=1) & (he_est'=0)  & (pc'=3) +  0.20588235294117646: (cte_est'=1) & (he_est'=2)  & (pc'=3) +  0.23529411764705882: (cte_est'=3) & (he_est'=2)  & (pc'=3);
[] (pc=1)  & (cte=4) & (he=0) ->  0.14285714285714285: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.08994708994708994: (cte_est'=0) & (he_est'=2)  & (pc'=3) +  0.3492063492063492: (cte_est'=2) & (he_est'=0)  & (pc'=3) +  0.0026455026455026454: (cte_est'=2) & (he_est'=1)  & (pc'=3) +  0.03968253968253968: (cte_est'=2) & (he_est'=2)  & (pc'=3) +  0.35185185185185186: (cte_est'=4) & (he_est'=0)  & (pc'=3) +  0.007936507936507936: (cte_est'=4) & (he_est'=1)  & (pc'=3) +  0.015873015873015872: (cte_est'=4) & (he_est'=2)  & (pc'=3);
[] (pc=1)  & (cte=4) & (he=1) ->  0.136986301369863: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.0958904109589041: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.0821917808219178: (cte_est'=2) & (he_est'=0)  & (pc'=3) +  0.3835616438356164: (cte_est'=2) & (he_est'=1)  & (pc'=3) +  0.03424657534246575: (cte_est'=4) & (he_est'=0)  & (pc'=3) +  0.2671232876712329: (cte_est'=4) & (he_est'=1)  & (pc'=3);
[] (pc=1)  & (cte=4) & (he=2) ->  0.12380952380952381: (cte_est'=0) & (he_est'=0)  & (pc'=3) +  0.009523809523809525: (cte_est'=0) & (he_est'=1)  & (pc'=3) +  0.14285714285714285: (cte_est'=0) & (he_est'=2)  & (pc'=3) +  0.23809523809523808: (cte_est'=2) & (he_est'=0)  & (pc'=3) +  0.12380952380952381: (cte_est'=2) & (he_est'=2)  & (pc'=3) +  0.02857142857142857: (cte_est'=4) & (he_est'=0)  & (pc'=3) +  0.3333333333333333: (cte_est'=4) & (he_est'=2)  & (pc'=3);
		
// There is no pc=2 (this was a legacy from the independent PA version.)
	
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
