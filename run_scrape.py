import time
import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']
DELAY_TIME = float(config['api']['delay_time'])

user_ids = ["9f5t66tq8xuf9sm0ry3gxbgan", "31qs7dg7jjyg2ja5oe3kpl4g3one", "7dmk731ndpctpe944rla7yixs", "31fqowjqnxi6utf42zwgdlg5kntq", "31tzvm4t2cpfxmvh6bjyzzciyviq", "31hgvvsrhh3ad66mhttql2z6xgne", "31hupd5sqypo4rvb5xzyg2cxneku", "31cdtm7zvl24qnkozlizry4u4b2q", "31mjllsa4msrmj7ke554bvc7qapa", "31nk5cjv5pom6j5qumxkoxxnxx7y", "31jofxeqgawxrzg5l6uhiws7p2h4", "31oklahay5xvu7p3ucz7hez7q7w4", "31wm4wommdlkpxkzk6t244wtbilq", "31vrmv6nwlgkpcv5o7vleesvfchi", "31ohuoekkm3r4swyuiqmchesgoi4", "31mff52smqm62mtxkg7kbcqdcejm", "312tbhsvrq5vlssk5cmznltm2oba", "31tjtjrefrtvfg6hmrslagl5e4aa", "31epbz65invgero37asxj4qiwmti", "mgmqh93kf526jsxszvorpl6c6", "fbcviii9nkht11nu9xfjcuta7", "31hoipusgiz43hjiy3cv62scfbq4", "3147ztqshi5j33kijyrhkvmzh3ki", "31bufcwidhdwe5ouz2rnqcg2cxhi", "q574dkj5bbw9s83d8krz6rji0", "31h55n5bgydetuad5myd6wvedit4", "31phxrxupltrczviq7rkljkprm5i", "zfh7yk758t07xele2fjrtxly4", "14mne2dmdjye4yxyi4hmjrhcn", "31k2gqviobofvtlmto5m4wfitmvy", "31kngabmhxxyd5xnulvwqcjlefem", "31f2kaonuqawi5jf3hlr72pqq43m", "31xpdsrbbjqbyb57uiqdtzxr4eze", "31isxjjaab7yvwligqbjua2bszdq", "31skygljx4rsnsw3f3ht7sghakdq", "315ig3hzzjoyf2orfhn3ewg7zrwq", "31hm72rmh3q6htbeaea6wtdn3a5e", "31jqvvqonuomjbubncgbijsuvkmq", "31bkmzpi6m27ft46t7grfzj32mde", "31d2i3bxrkrkn4gdzoibsgtytfr4", "31allkfgo7h5obuz3vvbm35nbdf4", "31gzzbjpwtnjha2wqe6okrtetblm", "31usrrekfgbh35ubv2eherpviixy", "31leej6zgfebzub3g24f5wst7ghy", "31ii3nkmfkde32ivyxfcxz4gkr2u", "31kfkvvi4ms3jmybw3r3eis52kdu", "31t4qvvihob2rubqspr6z32idihe", "31sfjylzvagaf6vi2xbiakea4fha", "jhx1fo9whzmdm9fmkzwvhad8u", "pandji", "31z4fb35wl3toewiwgwtzdh3i7v4", "y18yq74p3ecbdrkv9v0vvj940", "5a7ma5sxxvvccztr8m9gpifft", "31cvvyyojp663sdatxno47aeeysi", "11154757151", "wncaxmbwrykqq5pxqmga4ldfh", "3163fv3s7tzwagxnp5zcialif2i4", "jvwvvveid1mszsk71gq2rgxrp", "6y5bthnbcsfqpdu5xeu9gtey9", "31z3rvwckbs6xt3srd5zw5tpiave", "31zbjzyv6qgpng6yqbq3t7uwbdju", "31eu7u5lqrdirx3snt3asqenea7e", "mvz50i4ty9ej5rklwddwyy8l5", "b34xs5iqoiio0oehvf8t5kfci", "ap4hioyuckudoh7k11urkfl4y", "21jtz72sjw6xeadg77ic7ktua", "31b4giqqpm3dfxftao3fgenekmem", "31ge6467rxo6oibfnu6cb3yi7vvy", "31knxj7mgxweegbfkumspcpvw3ke", "dtur88yby10qri7544ui93aak", "pzits36wic4w25tllrm0wbafd", "31unwzmelffqfbrajvuiyk7lkjeu", "31nbkopbkcugjp6j46wdp3xoz4uq", "lpxn9d5iwg4pbhq8k2ihm2nmu", "31mhpxghjva2pmmtcptgxphvedfe", "31nspot7edzbtgjdz5pidfzpydf4", "31wslskrhfwnr6ogbkb7nowaxy6i", "81g6wst4po50z2rpd6v4gezud", "31muhxyl3avkifbyim5m2zisy3ke", "32otv0abuehsb702qytd7weij", "a395erh3qd0hit6yv7txltsy1", "31goea3sow5pyvchoi5cbx6jfj6a", "31ecy5yjhv2cu3fptq7op5awjzoi", "31gcoxw2si5lz3j5ums6skuie3vq", "kiksiqvvhlqpeswfcjwensmnt", "31sjbbtfgiyqo4rvjuizqujdybea", "31tmwfqn7u2j2af6r5odl2yyjix4", "31uaj33sg5u2bwnfcnsct5nmkkni", "313ypoeimkjcmyd55c3owcu273fi", "31koh6zn7u5377zifkmfaxt7lowe", "31ziasslio6xzsggtdvdl3grr6be", "31wrq5nzyv2kneeixhnlosyozoym", "adhqw2slhavypwaqr25vgbw2k", "vght0an6cxfe76xf2ixw8mhan", "xf6hs0hhh611vbk1scxxq1wxf", "31dgzoffdvzspc4fqent432qt4nu", "31pocgszvjtv4qpmcxkztjeei6zy", "31zmpyjcvq44mw2ejusfcwnnbtt4", "dv31odhha7zilp8zswz6b4uep", "zmkgs5bw25qtr2zckyh29892j", "570dhvaqdrm4dsfvo1ipalwax", "31ltzo32akgebjywku7kljmtruny", "lingganoviawan", "p3xu49ruf1ce8qid9jgqmaowc", "58grmhammx6s3cbf6py2na5la", "31jcr7plpxv5dsrwjfcl33sapmu4", "31tyblqirmbimqugny4pvp5paumm", "kc4ny34potz83ovru1iyav0wn", "315sr6fdc7atmwxaumi6idxpbq2q", "pd6ijhvfuxssn6a9rd4xojpwy", "31a6wd35u5ryrbqmeghltpfrnwge", "9zmn5q0gbpb8o67aldwj2jdh4", "315shypsmb45gg64pazrk3rcetoe", "0gdu7h2y1p1r27sx5y7wwqn3i", "31xcm4m5gzkqroixhs3iyajfu77a", "jfa9nmudrvzho9w7vi24e88lk", "31ne67g4hsccp7faaxkq5o63kfmy", "heo7nfg1prqej5t502x050gnw", "pzl4dsl6c77mo7bt2ow6itbjc", "31yp5i45q7ibfsjslp76dw4lfeu4", "31flbdlehffto7fs5ktvbja72enm", "31n3t3mfparqfwipshe7myee32xe", "nashw4aqila", "31szhcoxolpfo52tth5y7jgh5dwe", "31oi6236sqpb44o5mvkgfkobespe", "6dgs0w1unz1pz8ig4r2mi8m9r", "bfbii4f324u11vjvow4nhfjtu", "31idcvk3sf2qsjtpx6mbrlv6gsoq", "31h6yvlsconj7ddj3yrjjxydp7ba", "cz90ghirbz7mgru869di227f6", "6rl4oiocv9a5b9ri6zzpu0bib", "2w2ykspwsbf8dje9j286o0sdk", "315ppt6hzejphaj7wmrjbrtvkbxe", "31ggxy3trgxqkzmgucnp2k7elp3m", "lf0kshgvovom8m5ptj6kmv93x", "315bnuxm4b3yyqbc43hdvbu2p3fq", "31fsiuam57dg6njq427cpwllanxu", "31z36levqjsqb4sh7yznsckantem", "sdw0sw54deu2qoesyhb1t7612", "316zok6eo6okqpddzyljnrhuf22y", "31wpuuq74577cbagqbmtgiyg3rqq", "xvjwl5sqh59v2qghcz78cldf4", "314ink6i7vjgyih3lh6zy5pg3aam", "31xkzvwf2kysi2hfw7iuf4ikp6fu", "31ufly4srxscvaggnxa2mnv5hfca", "31mvvomfj2vqjtp5zldhs5xhklau", "31gghy2yt7ohrtdsb4qgynuhpbly", "kuiwddz9ixzpbl1quxojza40j", "4k4nd9thevc8ytu81ksj2hl1r", "31s25xgb3b3wm3scx7hht3zkfdui", "31s3txv4plyfgoz6kavmbtn2po4y", "ydsrmlxv6z3ztqfth4zwjy4bw", "3152tuxmvlqymw2wt7kwqlaiavny", "31nstnexbv7ym5yaqswfh2akxixi", "31tzunld4wpb3iqfvoha6t5pz4mm", "31w3vmnpvnhhtlu2rjqzsq73ec3e", "31uogs6bx3xjie62kvjbhx2rqt2m", "31knidxspstgity33dq225rljawa", "1oqb5rursjunf72v3id1ab1ce", "315nzoiiehltyu6gequ3mdlujbwm", "31ydqfrlranyga6zlsujxdovp5ni", "31ewuujzszk6oycfvdxmocmkudaq", "21lnfbiqeqrzymgc4ojgaicma", "31u6zl54z7vyl3vpxrzrwzzrx2su", "31hwpfhtjfzfcwyp7hjj3xb254iu", "ldyu1feykh4irg295ulydr0jc", "ok4846h7surtsexgixnroya8p", "gwpekqnlqh9g1aqbfc4tiivwh", "316uadraywmipsjft6tzmcpmwuhe", "31tmyug6bnzi4atqccwja5txmpra", "31poikhjhrzbweehy6felykw5yde", "hncirc30sm9hkpxsr7uldwxqt", "3pjek5924g25pq7i78fxcu71g", "31axd6px27nrhv7ztjvseoreuxwu", "31ihofttbm63ibjjnyfl5vcbjpfm", "31c2xv5ykq4tje3dlc442wmotkqy", "31rzffk3qtuye5g44rynknhabd64", "1jmaprnxvj8t2zek2z3pjqr78", "db44hkhq5kud5dsvgj90j29t1", "31y7otq6jnvgck5kqwlnw23qngn4", "31zo42hg7xwu42hxnazidtbhyu4m", "d5ia7z0q2b12uy9s2mubpq01c", "iafrtv7ubfwootcuva1r2a0k8", "31pscckyax72vdvz4ppimnpljgom", "314h3nkdo2hr4du55emgpku4b2c4", "aingfeby", "31u4yppiaunoy6vq3slrrqu7qmki", "31mfbgeeo523qfbtqjs2hky5grkm", "31o5oedf3xs2coxkf2wqcjdzompq", "d16ssaarmoy8dy9mkc5r2hu5k", "4fiaaj60p5wrtxq90aff6eepa", "31tjhmhymhctwmm4emkkxghkqeoq", "31coe6wchpsj3fb3ufywtbb33viy", "315man3jgkqfvdpspe6lkswqruta", "31ddydeqjt7heoh2lpd3oj4nntf4", "31b76sggmw64m2yjl2nuoee67a6i", "3156fh5cvawhqdphxwwpgoxcumoq", "31dopa4sxvijxjndwdqk7zavxwu4", "31zshbshpiqn4uz4k5o4ho2cqdra", "31ldkjcj3kjottt5omujj3vyyi5i", "9okyrnhjj3j0c2gwfx2akf2ew", "hebm3w0famft5mr9aw41m8uqg", "lucswioxo2ec9d9oopwst9fm6", "wc7jd2yt2pcgwozo22g9auc0u", "3134qooohm4yghwgbfqrbynl2rde", "uahqgac1poivblcogycbtxlbf", "31rpubnxuqn7kbm33uv4cgqha43q", "kaio3jlsns9ka5yp5rfkrm3ul", "313su5fpioeezkgal2mhkvmhezta", "d58yd9l4gdwbwwlss0s42n3zn", "ra3ll36ekkt28xva9g1w520h4", "31h56rp76qdqj2ll53zcfkwn2isq", "31eserlzmp4qtydfvgnyzebuk3oq", "31wn3adyeqrxlowq5sphzi2znv3y", "jplkkqun2b29w5fs1n8r0xfcq", "31zbjllx7crmeybyjnlyrgpnur4a", "31wa32a7gg5uiwfhwdsstwt76kjy", "31pqpmte7r7nqhe55kjjbhw7z3de", "31ey7pwluroi2jtsqicezjeh2m34", "31pgl243ot5rmlsclykuilwugqhi", "21llhkmyngr2wjazxgc7ds3ei", "31kfhotgpwibhza3crgkgqdqjmwe", "jx1l2l9qf8tuh12qifjgixjjz", "31gb4dzcp75qhwuleizbsyw5rp7e", "31beewvopbjgrhsn6mcfxvxe2uei", "21jkxwtsuhprjjs4vsv4tmbtq", "31gbvhmxfwhb6hxjo2ygnukzyv3q", "31d5sj5wh7hfy5gsw2ysnb4onirq", "31twhjt7z3iw7rfuva5ox2jtl3iu", "314upenrcql4imkztgk3tff7zk2y", "5fuhz1lsqj8cfc9watp9tpzia", "31iekekwpd5dmpyqkzo22gblg7pi", "u32s6l3n3vmrlm31eqh888kjt", "2xp4ndw6lxzkcwihsy53tvv4d", "31sygu6aoqlob27gkg6o3zawrwbq", "31bcpfhqgtddyjywyr4uczj6yb2m", "31qfqm4zveddewx6yf6dfxqn45vq", "31j434dx7qyma5lwg46ba3nj62k4", "lsqr8q97ql53v5mhhhi84tppk", "5buk2jo751xsbo6m4lfpffa79", "316rkfvf6gh6mvr67wjmvdevnqpe", "2n2z2j2hbk1k3bmxav2okjj9l", "31l6iuudmbpqnkxqsiuj3gowzqmu", "ty4bt0vwut6s6ksjf0tsp8t6m", "x4o3qg57t1um2q72w4e8h60qb", "gma1mcz1vs6s8l0z5axapw1v9", "14lh26ox32pz1g9bkria26bvj", "31foxqbaatxzkt7pksd5tdunphim", "31tlqt22dsqxny34ze3rv5j5nebe", "3172tvwp2yo3qjzz2bypudbmgfx4",
            "315naokjdsdkfz7uf3vvkjebqg2y", "314cm2zxmvvzygqgwjxg7izgup4i", "31rjpq7w24uhp5hwhn64obg3cj6y", "3144hcatrhalacnzzrb5lm4kp5um", "316mjncwi77q3suwwdanwwagrgie", "eaffdtj8f5korpb17hhzcrfxg", "u5aqlh63bs4uft8ej10ngh9tx", "31jfbjv7x6qiimq35vhcrg2obmgu", "g2sxbtyy0ukey4faz7rujxv02", "31uonchrsjvrzeo2faof2lxzcgim", "31n6i6ajjq3uw6ftunsoyybi3si4", "31oi76l6doossyi72anqo45dquoy", "smo7u3pm1wl017tj3beqd04ww", "31vvge3obnv675ywg5rdat6etjwe", "3gvckh0p6a4bzj9tu6850vpv6", "31ujg5nl3rjqrcn2kyeyfd4nhrxq", "312zhsbfqmazltsifjhlbukypaki", "31iodj7p7exghp2pi6sesf3ycuki", "31dm5hej6plwkeznlro2jsxfjj6a", "31ovvn7jii5exit2ogh3dnnk2goy", "wg5fyqhd332mbfdbjhnqgf7rq", "dgorwinx9e463b55li66siubw", "31ymm2crwfk3icmmeoyw3ulmlxue", "31rtggayns5bzmmztqbqe2lx5y5e", "31omq7yftqsz7mgcam5467y5senu", "31nsv73uq6rx7pjj6zlwae4oe33q", "31cajnh3ztnuisf5me6sxcmcyt2a", "31exn7zkatydj6gcs2wxyvmnb4ua", "31vwrt43chr26qpgg6g2zysjitfu", "313mydnnuyhtj4kbqitxuwx57dge", "31mfq2nw5gdrtoifrpovc6tnazfi", "31cy7extfb23ecxb4g3pullzrlea", "31n4hrj3dnabnwgxqwa23ema76hq", "p9fyaay50vpngm85s84q84kyb", "h3j6cmwilw2wfi4zqcbkyks2u", "31v6jx6r5e4rhvwadl2pez2x4hq4", "31lojcpro3uhr63334esjvnal3gm", "312hj6ply4zx6chk7n3dbsu2okdu", "710m5r1payq5yrr7nseypb2gf", "tlufgvdr7gqarp2mp1czcjezs", "31wbgaltexdcygzmqkh374ds6juq", "ty8z3gzhwy8yqd4mg0600ovua", "31jzwbenhhanyskvkn34jwulftvu", "31urwftyo6cbls52z5rxpqmqbkkm", "31roislfl7fm2q6scjidyopdu2wm", "wioh4jl78yg93h5diaxjjr71l", "31ptul5x73ezq35n3xln44mkevvy", "31qeuu2mntbzto7tj6hb6dd4wmsi", "x2vv94z6rzguukk3tmq4646wv", "31h2paqpa45idvlxpafj5slywnlm", "6om38x4dpb9mgfip5hdrug7kn", "31arkckh6bpjthzd362327ipnj64", "31giywk4agv42hpq7hthdrgjvca4", "ktfawpyqgpzl1a0iiz6m6c6h2", "ch23205ctn4hnudavam94uzna", "ai9ns4qctbuxqfuw9tyqwjy2u", "kmhedmmidzwa0z6iwvietfy6e", "31jvpwuwusoxlrdpqoq4gms5cj5u", "31yyknecxvo4cntljegyf3dhjw6a", "31xvvkf6zqepwx5qgol3qz42qpae", "i6p0ydyhsjrofawyyan8o7csl", "31j2nu3u44kwrpgdirqjapn3jwzu", "31fggzh2prlugv3422i2af4t7eaq", "312ainemt5kkcoo2lm5d7yus4phe", "mhjvnp4wep25ze9wfr6uyxwzz", "31fbtjnszoud5uuikah37iprssqy", "31tiho72gay6yzkofeg5pdm2fiva", "31suz4izu3nua6nbsyifw5qn45ae", "315hnua3wyrvcmnjzeffx4wl4q4y", "3hchkgqgar860ac3syioui8ii", "31fjg4wglvfdzhqye6icrdk2dxtq", "31xijocksqof7cp37k33u3axxxci", "zbtmic7c0b72u53kzquqn2jgy", "31hbhhc75j2xxx7bk5ceom4azdmq", "cwzltmhpo7p1ny35ik8rtkwyw", "6053ztq5ha9qouk6eemyuxitq", "316ahn4h4j6a2aidoelkuwslj7cu", "d90n1uziilffbez2p4nt0103s", "313xftuqka7vekwiminykisikuge", "31ig27jz44qhtbyiessm6espitpu", "yb4p0cwlnhipbvckuzbcfsk2m", "13xrrza3fw8k5j2terdqc0ou3", "31njh6ntuiy77cf2dh7lyitgo534", "31sz6ash3cbsm4vql52lu4vyvs5i", "rkpozlg09l4b2b1v664kf0mqe", "f1u3silj0ybgmyaw3a2nkn300", "31nnlrvwcatq2yclnjwvo4wvktdq", "31ekjrhm7u7sczj3s5wtkjsf25zy", "31z55pbi6zanlefy7mesk6m7wrk4", "kwqinf3qx85tpxo2nvadi3th7", "31o36sec5bkp3lajtn73h3vs5b3q", "31o6gn3nzwlp3kovw2n7czgrmiie", "p9xl7cgqeurm0koju51wvynju", "31a7ptvgf4soqbfhiqga5lai5gxe", "31aabywfguwaabhtkb7gi3gnfs2a", "31emw4kib6l4gqrrp4ea2gm3f5zq", "31my2lugvuqhadteiniptmg3tu5q", "p29vyr65alnsz5oa3bglkerlt", "31ltwthk27qfacgwldvj7nmmrzxu", "tppdwj0cs99w4s9kn7022mk0y", "3123fukgwqpmrvdwjkw2reumlci4", "x5un65a3nt9wai8o0f35jbyhx", "31rhdyu32fcpgfnfxpzst5t7yoau", "7sqvjtjcj9bvbm7uoxnbkxbtu", "31hg5744wgle3ufrccu6i2fobzay", "kwbuzor6722xg021xht4vwo6q", "31icwiuvzjvxmkztc4mc4lfek5ei", "31tatuynz3yaubleumhux2grpgom", "31mveny5ofhtrktqgrqwcclomg7a", "31va7mz7xmsvbiihyznriun4qbai", "31bpdt4lwtz43ov3lzrbkur2wpka", "31fwcghr7lzokcuna6s7js3m7dom", "uu8h6hy4t63y2bkubwtqfik29", "hyto0h4v2kiqf372xyss9ry7r", "31u2tfvv424th7be4cha7rwy2zly", "p4so735x25w2rm967psjjrdcq", "31qmjoqpw3kogaw54mcpvb5k634y", "31fbbbz45vpfkmubrqpjxi6vxqvu", "31p4rggi4yexcvsim2tnidy5gyxm", "31ouqxayqmush477gdanfisbahzq", "31ywmgzmv7aggvupqdgsls6jezkq", "gurxzh05nwmzehrs9m6xqiaru", "31puyycjkg5xenssgefh2xyi6lli", "38jsh448axrs58t41jmcqybtp", "31hzz3edixns4vobwx3737sk3sy4", "21jggsa7iaex3vedj6iyummdq", "31llczf4u7ikmxefn5m3d2i2csqq", "xrmrcz12tu6xslwpspyje44im", "t3krltomfdbfn8guy1ndc2y2h", "31tfj7ukxwh2uvumaetn7p3hgd7q", "313hyii3rfifjnfigagn6cnzh7sa", "31tznpc45rivato5ima7n7qkubhm", "31ib57srpcedciqzi2mky4k473le", "317rey6o6ltyrii37lmk5xy4bjwq", "31pgdayya7l5ci3pyezyneezmdxq", "ru8iowcn9jkc8xg1k9pv74l59", "0u2i1czckn2o9nh0crytzd4nm", "3133i5k4gzawezckjr2ncu3ztqsy", "31rgkecunyng4lsdrrkzxxjqxmbq", "31tmd5opqyktdjo3nvupgulp3scm", "31yeofrdlw453gyxooahuvv7ke6e", "314muxdjzfh5sv2a4rhfwlr3scjq", "51vzm3i0w9v083phr21p6m1a2", "31rhtpkkbk5mwelkf6n6oc4fgl3q", "31fbtftt3ztzbp3iu34rrwak4qsm", "clwo2eab6m7mzxugpa52h7726", "312bei3euwtfyiinbxg3jwc4g7f4", "3yiooz7ohaf5sb5pgfulprebu", "31pucavv2wgrea2yjuibnktuvd44", "31h6s5mrdhr6xugotqyrcywdw6tq", "31cnobohhvz4a6gi25e2ivcmqoxm", "31ikcd2nl4ryblwijksmu7i6awre", "31a2xawrxasntlorbbvvk7xloqcy", "31crkllqdtjunntddldfa2gdezeu", "31vh4ubtbv6hqnj7f4xdfidqvjd4", "fs6pitx1u2ev1z37c6i7rs6ak", "31oitedxssor7sl2e2ifpo62r24u", "31apgqa2iq3vn5qqh74bokcjcgje", "31ffynffjhsgu4h422ua7m4wxqbq", "0h2brcve4yaz6le5pyolkl5yf", "6ec6kh5fq9b41m3g1wzurk70u", "xeu26fsnaq7plk6abh4aq6bqa", "x61vcfssjtqu6fsi7k0pkgmzi", "31jjz6swcbxm2orakxfabewyci6i", "as4cucdntmq0ncijh1dv13cwx", "c503b4ilqb5chq0j00f42ux2x", "do928t3g01nezmsipwnf1hruw", "rdh2uz20v9j5lsiptlz7xtk4d", "cblhx6lh9q7awu9nwg8jjpfu8", "yd2uu0t0t74xmzh0oswpbbrkt", "31ra2xn3jaw6sx5o2bvrx4bhpb2y", "22wgatbxvyioedkokpfkh6gdy", "znvbupms1kcd36yejtrav4nm2", "313i3yokfg2wfjxaosmc4axfkndm", "i9erduboczjg27eclaanc8k2u", "316ddrsjrsgz4hdrqqicrqb6vdqu", "3163surfupjtbezpon433riju654", "31jqexn4gqb2t3vl5e7s2j45hlc4", "d5lzwsqzb3tos8py1878jaz6t", "w50f8f1lio48y4yena5rhz0hr", "316epl6rw3ro34x3kcypipvs75la", "ggcq6oigpov66jlfp40m8vukq", "31q7p25toeqjvdkszo6uugfaxfvm", "31f76k6llm7h5nisfkltbie2ejxy", "313xxlvqbzjca3zqbyatan6fxf5a", "31djplgk4ge4h532gsehva4mqh5q", "31yf2fifrgqf3vjwcenyy73yvvxe", "21rut3yvaguhha6xnujcpcria", "50tidsvdg5vzvlx477zu77k8z", "3122hx45banrxmqxfjjbaaqtmpwi", "lqnvwz7muf8qrgeu0uad0v2ga", "lvryvh396t6mj2jhaat3n0vqv", "rk2h1bi8yuhkg0n6proaobqkb", "anandadini4", "31khl6fq77jw5f33aoef36r3vddq", "vjz5wwxrlzhbre06dzz7ok9qb", "budshhmcarzee39bobe9qldhv", "316l2dubvh4oa47fb35duezcej4u", "31yk62hn5jmd6nrbahf7ie7qjbtu", "richrdkurniawn", "31xx2tx2kylpartkzduvijkkio5a", "31c5x3vkox5247aipuff5zqylm5q", "a6liq6fpskkr7nbpp12g0w1qz", "31rfcdpjksqpeo5y6yuvuo3zmt4e", "31rboyndhymlwyyrdh272aiqpyiy", "312e3yhxf3rcntawq2dux6m3qe2y", "plpd012c5fxhmqj8h83ybbv99", "31hhu6bgi5i62vugbbzjbtsbcdke", "31y5s6avtxunbnyemiczr5bevhte", "kuqrwhkrov0jctkvr4ntzktke", "31u3ijsuja44aneihsg2guznwbce", "31z4j6a6soch7jeochcqkcpewgti", "yye4kc6f4hkd5egc137wr13u4", "m58k26et8ds18bqyv48o9odbb", "31kuy5z43xbrt7iu7xmrundhuf2m", "31e7gtcppmfwgub72qcnzuhtuuqi", "inkafad", "31y2mo25aichegqlzxgsq77tt6cu", "31qymrt6ssjz4qud22jg5ksxug2u", "ayke8ec7bnr7hwouxcfidj242", "yc1xcy4mi66idnho1ot74b1wo", "31zezwy6qyr3y7c2vjma7fhdzttu", "314bl33oxovinoneq6demd5y36xi", "ce0obfetwz33sbmobvxo7hlzc", "31ecfvgoghw25xwv7klhwk6kdana", "31uvefw3v2rpjbvdd3yddthkvlma", "31pstm2iuaor7op5gtzhepdrseam", "kqyfyd7wq1mdjy7323xywf2kj", "nk5x7qpln3csd864sq297ffws", "z3fd1lm8z7soyexpjc8kljwqs", "b2ljppxc8vbej8n3mzm5bmotu", "bwhqnxan7p9e5sc9bg8rxs1nt", "31buch2flqfuhsv6jhzz3bkftup4", "31powd47lhzaufdaygjhlhrnblfu", "31pmual4wzisuaqc3hdfyvxoqa7a", "5fmzxnv74yzefzlajyswgu5vm", "31echrpvcemdvmdcshgudrhx5vm4", "pn2vesv93a5q269r34lccpkez", "31eam2vy7772aihpjhytotx6pj3u", "31h4lys3fgad2kbnnswrauvmn5nq", "31jee2zubg6axdly7cyne72logym", "o2jtrm6vm5h2w8midy0id4ru5", "31ig5lrlziswvin5lgzpnptqmuya", "31f7zbpqpkqid4f2yfdy2h6hwwaa", "7vihbjpp15b5lszjuk2szu7jn", "31mzw2cinfn5wf3cm3g3db7ipmi4", "316fq2cnprqu43yfrybwfhtmz6zu", "9pxubeg6ekdunumzum09zpiza", "31m65zv3zvnuhq5d6oo3636z6yfi", "qkhwh2zeux67q6gyc99rmiqzs"]

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# SQLite database file paths
playlists_db_path = config['db']['playlists_db']
songs_db_path = config['db']['songs_db']


def create_connection(db_file):
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs):
    try:
        offset = 0
        limit = 5
        fetched_playlist_ids = set()

        while True:
            playlists = sp.user_playlists(user_id, offset=offset, limit=limit)
            if not playlists['items']:
                break

            for playlist in playlists['items']:
                if playlist['public']:
                    playlist_id = playlist['id']
                    if playlist_id in fetched_playlist_ids:
                        continue

                    fetched_playlist_ids.add(playlist_id)

                    playlist_details = sp.playlist(playlist_id)
                    if playlist_details['tracks']['total'] <= 5:
                        print(f"Skipping playlist {
                              playlist_id}, not enough tracks.")
                        continue

                    # Store playlist details
                    cursor = conn_playlists.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO playlists (playlist_id, creator_id, original_track_count)
                        VALUES (?, ?, ?)
                    ''', (playlist_id, user_id, playlist_details['tracks']['total']))
                    conn_playlists.commit()

                    # Store playlist items
                    track_ids = [track['track']['id']
                                 for track in playlist_details['tracks']['items'][:24]]
                    playlist_items = ','.join(track_ids)
                    cursor.execute('''
                        INSERT OR REPLACE INTO items (playlist_id, playlist_items)
                        VALUES (?, ?)
                    ''', (playlist_id, playlist_items))
                    conn_playlists.commit()

                    # Fetch and store track and artist details
                    track_data = sp.tracks(track_ids)
                    audio_features_list = sp.audio_features(track_ids)

                    for track, audio_features in zip(track_data['tracks'], audio_features_list):
                        track_id = track['id']
                        track_name = track['name']
                        artist_ids = ",".join([artist['id']
                                              for artist in track['artists']])
                        duration_ms = track['duration_ms']
                        popularity = track['popularity']
                        acousticness = audio_features['acousticness']
                        danceability = audio_features['danceability']
                        energy = audio_features['energy']
                        instrumentalness = audio_features['instrumentalness']
                        key = audio_features['key']
                        liveness = audio_features['liveness']
                        loudness = audio_features['loudness']
                        mode = audio_features['mode']
                        speechiness = audio_features['speechiness']
                        tempo = audio_features['tempo']
                        time_signature = audio_features['time_signature']
                        valence = audio_features['valence']

                        # Store track details
                        cursor = conn_songs.cursor()
                        cursor.execute('''
                            INSERT OR IGNORE INTO tracks (track_id, track_name, artist_ids, duration_ms, popularity, 
                            acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, 
                            speechiness, tempo, time_signature, valence) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            track_id, track_name, artist_ids, duration_ms, popularity,
                            acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode,
                            speechiness, tempo, time_signature, valence
                        ))

                        # Store artist details
                        for artist in track['artists']:
                            artist_id = artist['id']
                            artist_info = sp.artist(artist_id)
                            artist_name = artist_info['name']
                            artist_genres = ",".join(artist_info['genres'])

                            cursor.execute('''
                                INSERT OR IGNORE INTO artists (artist_id, artist_name, artist_genres) 
                                VALUES (?, ?, ?)
                            ''', (artist_id, artist_name, artist_genres))
                            print(f'Updated artist name, genres for {
                                  artist_id}: {artist_name}, {artist_genres}')

                        conn_songs.commit()

                    print(f"Saved playlist details for {playlist_id}")
                    time.sleep(DELAY_TIME)

            offset += limit

    except SpotifyException as e:
        if e.http_status == 429:
            print(f"Rate limit exceeded for user: {user_id}")
        else:
            print(f"Spotify error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    fetched_users_file = config['file']['fetched_users']
    fetched_users = set()

    try:
        with open(fetched_users_file, 'r') as f:
            fetched_users.update(f.read().splitlines())
    except FileNotFoundError:
        pass

    conn_playlists = create_connection(playlists_db_path)
    conn_songs = create_connection(songs_db_path)

    if conn_playlists is None or conn_songs is None:
        print("Error! Cannot create the database connections.")
        return

    for user_id in user_ids:
        if user_id in fetched_users:
            print(f"Skipping {user_id}, already fetched.")
            continue

        fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs)
        fetched_users.add(user_id)

        # Append user_id to fetched_users_file after processing
        with open(fetched_users_file, 'a') as f:
            f.write(user_id + '\n')

    conn_playlists.close()
    conn_songs.close()

    print("Playlist scraping completed.")


if __name__ == "__main__":
    main()
