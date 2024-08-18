import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load configuration


def load_config(config_file='config.cfg'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


config = load_config()
DB = config['rs']['db_path']
CLIENT_ID = config['api']['client_id']
CLIENT_SECRET = config['api']['client_secret']
DELAY_TIME = float(config['scrape']['delay_time'])

# Replace playlist IDs with user IDs
# Replace with actual user IDs
user_ids = ["313i3yokfg2wfjxaosmc4axfkndm", "31sygu6aoqlob27gkg6o3zawrwbq", "cn09bm9fkklq7w495bzzow2kt", "d0dayhvjf753h1smgvhy758mo", "31n3cj32ba57rsvqv7mtiegzlthm", "darren", "31mmf6ap6r4vy376zzojbvfqxf5q", "31r344ruxdvqxxdydflofdwgagcq", "316ddrsjrsgz4hdrqqicrqb6vdqu", "31f5o2dg3o45zvucn4u7ikif7es4", "4kkkslg2sk8tml1q4nq7r3www", "f76p670rl9jcm5o3wmawiwhbu", "vp3t7vvs8c74g5600794wiq54", "315xookydbvng7w3zq67zq4xh7r4", "3134tax3y2v5aedm7stgzgdytfuy", "31eam2vy7772aihpjhytotx6pj3u", "6lz4q9tg4h6z79tpl8j1ywdci", "317hscv5fletl5zsyeggpbkpgfsm", "31xwjhzmzqd5m576xsw4bt6lkifi", "31uzxsoyqzjiu4mwx4fjsjrv2dym", "0hb2ch7sc4iup7n656yvaaw8f", "2w2ykspwsbf8dje9j286o0sdk", "8f4sw67sktycx1b8acw9srqk1", "xpfylr22ahdq63bov8tg076o2", "314ink6i7vjgyih3lh6zy5pg3aam", "31pa64ojr3ygv76evs6niyuz3b2q", "31lr4tqolutgtrjkaurzhtowxjly", "31sq3s4dqexxwaan7yp76rowwtyq", "31px4ervdpeyekvridefj6bu7cjm", "iccr11vr5t31y0jmh5v0uzks5", "31o36sec5bkp3lajtn73h3vs5b3q", "pjqzf9jnzn541f18na2dz83to", "y1ps0mnd95mtzwydj0epgh5i4", "313g5rrolcwmx7durf4ymvqv2hbu", "b9f8womdop4dywbdl58uu3twy", "8rco90ormb843tfrlppzf6gdo", "te8w47rjmz42z9n894paarmsk", "31wzvpf7kr2wgncb5tiaz7e22fei", "314bl33oxovinoneq6demd5y36xi", "31exco6c4ffon3evy2brzdrf4ica", "31bfstfzuogteqlzixwn3t5ustky", "31ramqb7lbgdrmi3z7hr3jt4nrkm", "eom65t8uj4n3fz7kmbgvxuhxv", "3165inzy3t4huii2byylkas2ys4i", "313loe7qwwpthv6dmblkvbsyqdim", "31vvge3obnv675ywg5rdat6etjwe", "ulx1qy4re4yujyvzsdkt0uqa7", "31cvvyyojp663sdatxno47aeeysi", "570dhvaqdrm4dsfvo1ipalwax", "sqiaat3krtyv8cqk1ywa4z5b5", "21jtz72sjw6xeadg77ic7ktua", "31epbz65invgero37asxj4qiwmti", "314kmnx7lzzxyhdz4rapok2b7ahy", "316wzzsckzn7uveweafxzud7fy5e", "31oo5fape7bpwdwtzwxevegzh5nu", "31vfqi547vy26k7g6pahinzseude", "31iencsxzwxmtorukemd7naiuu6m", "31iixaqmzoescqp3pz3majvu7lwq", "31yad2h7ub3qoobu54gjrodjtoy4", "21lnfbiqeqrzymgc4ojgaicma", "315ssvkeqx4wzuj45zlipfft5keq", "4htkrnw2lmftp8eh8rsmyiz0w", "xrmrcz12tu6xslwpspyje44im", "31k2gqviobofvtlmto5m4wfitmvy", "rw4vagqb5jbjak0kx3rwvk569", "18nvye5bd68pd5kepdysffs23", "vbktjlxjcwmeqpqk6v6vixncd", "tzyv1t8c6h97v3q5ntariciah", "31dgbbvz3f5lns5vkulrutjzxqvy", "kwbuzor6722xg021xht4vwo6q", "314ilajwouji467rrgtyqr67lqyi", "2pdnq1e1a0ob2zaiqdtoadlnu", "31d3e5bigcxra6zfulmrdysk26py", "31647ncttaoso4kqsz6aoidyqatm", "hcmc7lcdjzjqoja3ajxsfz79s", "3175pktg2txgniasz3gx5c6tsufy", "31soy33d74vimxrsems5aumid6ge", "16h9eo8r2iy22ykroiyyy2x2n", "31okybx74xxxmx7v4hz4vbuf26xy", "31wucblyy76dekar2mk7nsbfvtn4", "31llyvqphwnabmozbtz4izphygqm", "31xhzgb6aqxwmd7kaxc3e3qztv6u", "3172tvwp2yo3qjzz2bypudbmgfx4", "t0al3bezb175dw4gd1cq8m86v", "314qaqz5kkqb423k3x7ttluf2iva", "0n90hd5wjyjr9y9uvbawqools", "31nspot7edzbtgjdz5pidfzpydf4", "31vh4ubtbv6hqnj7f4xdfidqvjd4", "0adxiugbdudcgcf9n8kw62u0h", "31koh6zn7u5377zifkmfaxt7lowe", "31pkrtb3n7z7hze56mrnpam7lfoy", "31e5vcs4clszlr3buoveahzishfm", "nawneu3vgn2hi091nq4n1a4rp", "31yosfvhjuegclvkz74jfxe2nmze", "31zsn5s4xbsqsavdzxxqlux2xubm", "31usrrekfgbh35ubv2eherpviixy", "3ln9d67cln75bblv2th4yldro", "wh55c781sy3l4yw21k51nldcl", "31vq2ck6y2k2vrcaz7qu5x3viud4", "81g6wst4po50z2rpd6v4gezud", "q4y56toadukdjkeb7i0bq2ow1", "j2r2nz9pxskup6zysxyg1jgk4", "31zubfma34pgvmn2pphree6ee7me", "31odu7vm2b3d5jx5bh5bhvdy4tpe", "kaio3jlsns9ka5yp5rfkrm3ul", "31ktjhebynhduqdnb4k3bbnvn7gu", "31zvsx4irgjrqsz6dntyxuoh7z7u", "31akjuish7mhhsjdcufuw4sqotia", "31vmxixfnz3f4hrlo5xwvk7alute", "31hkmyu35wubu3rg6vx7jkwczqma", "31cjmyjpec3jwruhwj6hmwwfo7wa", "31unxvjxsf3sonsoajutqfs5boae", "31o4xg6bq4hujd7w6y26oymfwpee", "317njgu4w3dn6ca75e6us6m46yee", "epjt6axcbkbvadfmk3ppft6b4", "31r6aueykrmytbpz6jk26yotiwdy", "316q3fhxt6bz374dzy5dmarj7xp4", "31hzz3edixns4vobwx3737sk3sy4", "313i62mb3geedvg4wc4dxvfohxti", "nzepa791aedrlrhlfpbg5d7vs", "31v6jx6r5e4rhvwadl2pez2x4hq4", "314c2hanxqpuogjzzqxmf7rywd5y", "312thwj37cobxquqn5irorwdsvtq", "74eycl7b9bzok60zf8w2ogqnn", "31meq6jug4pbz2755di4e5kucs5a", "31pgdayya7l5ci3pyezyneezmdxq", "m58k26et8ds18bqyv48o9odbb", "31fd222x7bgr2brkjp46m2xxlzpq", "31au6afj4ohqrw6xnygszar5m2ey", "31h3zugea4dr2vheir5tq36snjaa", "ty4bt0vwut6s6ksjf0tsp8t6m", "31kswwjxmjpigdm2br7fmp7logla", "s0vncc3f5t0tmwepihj6jk5ar", "31fqowjqnxi6utf42zwgdlg5kntq", "31snkaolwckymoqphx6pqsgqopii", "31ooehqhckhdsejlgun3zm7olzbu", "1hz8vp31h3hncyd5tuafs8v2p", "5zkx1upmyabkhuknf6ovgrov2", "315h3s4cbtmtqnf7plvxhgs2pope", "3152tuxmvlqymw2wt7kwqlaiavny", "31roxarmk5rqkn3gnpdzcucvu3lq", "6pgtd8266pcvypwmthkbpdrng", "315shypsmb45gg64pazrk3rcetoe", "317bs72djo35f3a23xgjewtzzuam", "31cajnh3ztnuisf5me6sxcmcyt2a", "piqxil", "31ii27ak3r7fnwipxv6scsv7nroy", "317w2uirm3napnv2sczkoqh2tes4", "31naqjfv2ugx6vltm45l3busk5em", "31xnh2lq56ify5j5o4qh3hj2kbva", "31sz6ash3cbsm4vql52lu4vyvs5i", "31tpskdoxdd3hn42xt7qglsxlemy", "7q32tee1602l5thhessz0bvc7", "ctc049ecp9u96kkcn8vp929ag", "6053ztq5ha9qouk6eemyuxitq", "uahqgac1poivblcogycbtxlbf", "hyto0h4v2kiqf372xyss9ry7r", "p58hf6c4ywu7ovhfti0t8wkui", "31pmual4wzisuaqc3hdfyvxoqa7a", "31ozfjh3fv2pz55spddiokrlpf5a", "31ihofttbm63ibjjnyfl5vcbjpfm", "31tcm2mxvpaijnr22rerdk7wrpzq", "jgxxmpb2bf0nqfniouw2jv83r", "31e5dilb575ybn3xzh2ny4jcs77y", "31q74rij2p6hhukpmuevwjkcniou", "31uuorxk6i72tu37or4nltid7h7e", "dv31odhha7zilp8zswz6b4uep", "31rwyt53mzjnxuvmpkmt2ubeead4", "fctwtjhwluss52dh3zu25a5lg", "316evvtmaf6qapnqgdu6ygz225vi", "7e5e0h7f0shz1m6nqkp692nw1", "31tucvl2ejkbyt6tj4slaf4v3i4e", "ij6kna8cz2uoy1dimumd8yd8i", "31bzheglssgo25ysrrjclsjypa7a", "aeob353f94dwomdy593wp2vth", "31pc2gmcumznb3oodfm44lex4yr4", "31qfqm4zveddewx6yf6dfxqn45vq", "31rtq3gtgid4vg3qfi52throtrba", "31dwojcjgwcvxunh5dmaj2eyrwpm", "heapr3vrk1w4oo0bvddsdsio8", "31sukxdln4xkptcn2khg3hjdupxu", "ranggawari", "31lucuv2v5rmtdzrxsqusovbirgq", "31dxemumexytwsh6ifg2jpxwpcqi", "313b5izukwew4lm2qilryym7vwvu", "31nolc47bvwaufywngxaxdngl4ve", "31zr5kcaeyfy4yk3usgonodmdjba", "x2vv94z6rzguukk3tmq4646wv", "316ukj7wrxmzrru5imz6xhbgycz4", "31ss5jxh3hgd4gztgqpbirhctfhe", "313xftuqka7vekwiminykisikuge", "31yk62hn5jmd6nrbahf7ie7qjbtu", "ndw6w274kz385rwvi1mmz48sw", "rche2d62fasog2lx537i183fc", "31urwftyo6cbls52z5rxpqmqbkkm", "31k4y63ugmvs6rlpjdvepl77odbi", "dt0833u6rjs4cuqvvg386oyci", "valspire1", "eaffdtj8f5korpb17hhzcrfxg", "31s43khhrjh2a7nk24sxc7zl3zcq", "31cvwzlt5q6k3tko73mrtyzqcmga", "31mfq2nw5gdrtoifrpovc6tnazfi", "mhjvnp4wep25ze9wfr6uyxwzz", "q74ifo0xxx6v6gojxiuv15lc8", "31wh5yqiedycw2toqccadyousa4q", "31ikcd2nl4ryblwijksmu7i6awre", "lingganoviawan", "zeopnw8lrenk2ivw08b8747e0", "31cfuyysk6zpb5urnyqwg4y5skpq", "31ieoubntmo4l5ae2bdpd354jeoq", "16ogozw2uhepbwqo22v7ygbxj", "31kn76hitfgzqnjigithryxrtqbe", "31qlbgfetsh7rxtfen5jz5ke6hoi", "kwqinf3qx85tpxo2nvadi3th7", "316nzj4uhpjamwlhhgknrvjlt3dy", "jtpatakdguxqc8mryixenh05f", "smbyeelc1qooj8wd7m5ts35wy", "31cdyxs47bj3kpo3mlorhjb23epa", "31pnj7nnp2fh7p4ur4wplpe5vdgu", "31a6wd35u5ryrbqmeghltpfrnwge", "31m4ylwbfbmxv7e2bldqzet7mteu", "31t72hkj5zrckyxqo5d27dnitg34", "31ioocbgmzfpverohcnx5xkschaa", "31jfbjv7x6qiimq35vhcrg2obmgu", "rud82625x5sr4zeuthcp7gdei", "317tfx2cdmvnzjfqd343bgdpkh6m", "31igaixwwqsuw42mxko4hyp7jrom", "31pu4tn54cqp44wzye2abymieekm", "31hksdtg4yqtekwdawqqm5bmzrnq", "31ncl5i36g3nv3u2jbn4fozxhvme", "31xk5tvypso3gjtgnzaslckmkj3m", "do928t3g01nezmsipwnf1hruw", "31zbjllx7crmeybyjnlyrgpnur4a", "31vzjlftil5sxtfnmnvmuie65vke", "aeis4av6xxknwhmrufjvmurg5", "31hg5744wgle3ufrccu6i2fobzay", "31olebkhujpbtg5xmizaa2clkyou", "31z6qatny3sdkqxqhhaziqa2x5ha", "21ihwxezo7lywxyqee3se7ixi", "31nhq4wd3epgw6vpfeb5ewk2ekmq", "12100671397", "uaxrx5n8oq6ik39d2s0pdrsxo", "0ysmoqpoixmbnbuh1k6j2bmby", "31barbonialcnz5rmtekgx6ibcxa", "31lnrpsmkrmevtzsymby46go26v4", "31f42vpcr5kphf7tkx4kncwh3kiq", "638isqv5lu3vlu6yqalw61j57", "ze22ksou2xa4pplvz8eq4e5q1", "313voyadrdwxz4k6larb2ey643sy", "3qszfnojuvrnl0r4sh0b4g09v", "yrmiflfuwzayh1grscfmv84ia",
            "k7nb2ou6s35b8n7iuaezwzj67", "31h5f3g3525wktpr3klrlz7okeiu", "31xqjnojufrxnrpcd6cwbprx7zjq", "ejm3owujrjfa5b2p4b6ag6hq3", "jmzmyzeuockwvypv7kdo2s1qh", "oqg2ag1yur5c7cclbhmo69ug7", "4fmrk9vvdz2dgmey7f4y9o5pg", "31ebbkdzmlhozmei2qw6gvu5qig4", "qn1iwxzzr1c04m56nra1tlzo9", "31rvf5fk7gjeshmnfukh5pdy2bve", "31w3tbfww54n4o3a5zms4gethh2a", "nipacj20xy6sqqd29b5tc3vxk", "31ggt3vbyfo3hi4qgqqaun7wovda", "31uft4f2chuua632o4k2ecrjum4m", "314cwets7m6yy63enzun7a7fs54e", "31egbm5vjdknzrmb2yurufydgwaa", "31iekekwpd5dmpyqkzo22gblg7pi", "31bjrtdqkaunrndkokiee77v75se", "31ay2furjrc7lp7kzvgo4keuygsu", "31byz2auxtpmcwqhebremwozvctm", "31y2mo25aichegqlzxgsq77tt6cu", "31uc2nubdxjqhs6vty3my2bezvjm", "31tcrurefwvjccurc54ury4w7c6e", "31tmwfqn7u2j2af6r5odl2yyjix4", "31h6ecq3s67ag4f2xp4xpzrpsegi", "31muovzigmyep66wm4nueqcj4bzu", "o556zq4tfzra3qwimgao63g5i", "31d5sj5wh7hfy5gsw2ysnb4onirq", "vwhdfareccwjtn98wb67fk3de", "31ebzeurveo4drqgu2cumifrfruq", "31fthnoaskjxf5z6ylsxpjbhlw3i", "31ke45sv7lg3sn4oc7pslblkuhru", "31i6iyz4az25yfddhojrkqfeu33e", "3v5pfrewev99uw2cw6nrmp171", "hnadnlg7vencmfopgc5xvgf2p", "315man3jgkqfvdpspe6lkswqruta", "aiwx031y3ue7kjujr4818ifuv", "225a5kvzv7vcgr6zwyxcle5oa", "31bbvmpa2efsavzk42hxuvsrtqva", "lvryvh396t6mj2jhaat3n0vqv", "gnssbeauty", "31lojcpro3uhr63334esjvnal3gm", "wb16nbmw51fu975ez21vtn0n9", "312mcmlgp7j6uzcumbvtkw2dbu2y", "31d6np7jtzt7wbu4tg3rk5tjffkq", "31jblatfubkqxppr66mw3ggg7mg4", "31efsmvjsydhavuij3rykcv2qng4", "31dm5hej6plwkeznlro2jsxfjj6a", "egagsqm6xfudhoko3a5s7l5sj", "313x26hm4mzscepgh7lbj4crsdse", "31aeswxc5awrmrohpbjnmnc3aqoi", "31x6bmxvtbp4mqt44n64tcjnubva", "sdw0sw54deu2qoesyhb1t7612", "31wq3d6qrpnuers4koifdatdcxl4", "31lvzw4dmsd6u54cmlrg6g4bqqee", "31hwdmnxaj3tbqlonm5au2fr2sfi", "0uf3sic0p5dyk4irapnpedy2p", "31oi6236sqpb44o5mvkgfkobespe", "4m3q62ze6resrocj6e6nsc7zu", "314slj6pgnz4v4u2mpzsln6ghjny", "fhjhul7pnvn06o2bt4to6wjcz", "xk4fixlthsdbxtps3kictbnrq", "31ig27jz44qhtbyiessm6espitpu", "31rrqbunchlc2imrkknw22ufbz7q", "31frvyxjaahc6jdgxmgcu4iyrp6e", "316f4ad24ijaemnx7rcmlz4jdx5q", "31tga2qnnfhizb4fczcbmydjfrjm", "4xd857pkj2373l3tg0g0p4t30", "nr8c01a4t79bz88pjmx0ds9jr", "3rlyj6fvq0g4s2moa8eyw4f79", "zhn1z5mxf8m5g7kv159m1w6rc", "312zhjx2lgm46tjmciuclm6etway", "31na6l7qx7wxn6oit6a3dpb7s54i", "31shc7kufd3dqnb6w4x62ica7dqe", "fqiazu5mdc38ofr4k338zc8ec", "31uvefw3v2rpjbvdd3yddthkvlma", "zs4ptmqj5su4799omo5doqqc5", "31fbl2g2jr4dtevb4mwgkj5e66oq", "31zrch6u5dqqnp6lasvfnh3nkhs4", "31nrarsnk4h6mlij3oa4rlgycjna", "313kfmev4ikkpngfdbyur7ngfrue", "3hchkgqgar860ac3syioui8ii", "31u2b6tndzx2vm3bvit46wdjotki", "2p2d54zmtua8eslw335clhbrb", "31ksu2v74ggy5owtwddqtibq5cwi", "8l8cbwa0x9kh4lfwj0uewitoh", "31epzxvv3yihjl3y4ytaodgu6ncy", "31jfwzfpy2zfam7qws37dse4us2u", "31qeuu2mntbzto7tj6hb6dd4wmsi", "srap1bfq2r0eskfyrkx7xpgel", "mrygx2c8ooqro6bj3ompmjme2", "31nbnv2pi3fp6ydofdggspn2aa6a", "31j3zypmb5jcy2bcatpoqv2pufeq", "wrx4wl2aal8s384yk2452qkj0", "31axd6px27nrhv7ztjvseoreuxwu", "5a7ma5sxxvvccztr8m9gpifft", "31dopa4sxvijxjndwdqk7zavxwu4", "06khqj41bk3ghe55gefpqbgc7", "2n2z2j2hbk1k3bmxav2okjj9l", "nn2p9o82s3scz49n48go1gx49", "315565s3cobyuqzf7yv2jxgcxbyy", "h8h4kn5g8c192qydsxupkxx7x", "31suz4izu3nua6nbsyifw5qn45ae", "31fempqf5ognljhvlycak4unhu7q", "4pgu6ucdgjqpgzaay8eup261l", "9pg3l6j31z143jlyvfodw8eln", "312mbjxz7sni72d7yjwcesxjvmua", "mima4jeg4ktxoarl5to0fynkr", "3sbdh9vbw6i96lfxqifo7rh5l", "31jt2mbieew4hxatagtduvrcmmva", "312ahm5ytr6dhlrb6ieaathijrgm", "3133i5k4gzawezckjr2ncu3ztqsy", "31zyqvckn5sxvwvcwv546bxgqs4e", "31sg2g2eo5hcopujwvbb54ahchha", "31mmpqgrd7sb7sraxuapyyx4nxoi", "31u4yppiaunoy6vq3slrrqu7qmki", "31ioa7uztcvvojrxfy7elgj35pcu", "0uy37eclqqakgv1n0c0crf54p", "31u5sf7p6435luwulb3v6wqd4ija", "ohm114zciwlcfjem5269pxyis", "31grxkfjmsvohp3kuyooaj7xtvcy", "31iqeyk4bn73ksgglttpev6vcop4", "31qgytspwgkpdvqqxhuov6tw3kyy", "31uogs6bx3xjie62kvjbhx2rqt2m", "14mne2dmdjye4yxyi4hmjrhcn", "xvjwl5sqh59v2qghcz78cldf4", "313runtsaequljmoen4xuys5wixy", "31a3rc3rsxcrmpec4nmlagt7uxem", "31ibicp6dr55ggwomuhswusnzwiq", "31jbxcrl7roa4yl37gdjvcvwadqy", "ib2ha74usm9mi2nccnicbfwt7", "31eykivj2aodpuy4lrdy6neranmu", "31htgilkd2723ma37kiv2alreo2y", "31fbtftt3ztzbp3iu34rrwak4qsm", "hebm3w0famft5mr9aw41m8uqg", "31hdqv2lwo5664wh2prbbpcrdfmu", "31uonchrsjvrzeo2faof2lxzcgim", "3z5fc5lwrpcyij812uwm78vuy", "bfpi669bi2xp58xfql6rqpp4u", "314r4og7eeyovaip3jfsjiphx2da", "thumc7rs4astcpa1n6hczq5lm", "31nnlrvwcatq2yclnjwvo4wvktdq", "31jtto2puk64wpouyk36j3shlo4q", "6gdoldu50h6z0pdca6nfu6nh4", "cintiavalentina140206", "31qgo47pftcn6yyxmc7qwp4eziky", "31ohuoekkm3r4swyuiqmchesgoi4", "31pxdisrbgoczmugw5mcqpmbvwqe", "31sscsenctsj45mnwcjcm7ucuw3e", "316y2a33nwhegp2e6v6o2wkj2uwy", "31zszze5wephtknu5fdk57lk5c6i", "31qz7ejqwytb5pgk3s36knoubejm", "31kefj27c3astocud7yc65ibusyi", "iafrtv7ubfwootcuva1r2a0k8", "1jmaprnxvj8t2zek2z3pjqr78", "31dypk43s7kzsw5gbhtnyjnah36e", "31z6nc725by42emohumlwwborqkq", "31quzdxd6es3gb4licewp5cr3unm", "31vlx63xk6yskprn4wifxtg67kae", "31rrsokkiqt7e2f6q4arwjr3wxbi", "317f4sc245appxkjfdgwesb7ugsu", "31slauliehsq4yurpjvlcg5o2fdm", "31vq67blyvtehgstkxh5brg5dgqy", "31tpwy35q3uprajanpzmljl74u4a", "31hkducctoailtomtegsbm7qqupa", "31yirpvuyw47kknqlq4sf7fjgft4", "br8dtaspjuo020l8e2v2v0ibi", "31qbv7i7rjvdasnb4iy4a2im7lfy", "31v42wic4c32cbgymj6r4tcoumza", "31hyfi5cvdvr4lkg3wwmqb2k7any", "lahiti4olm9v312hl59rlkvw7", "31h6yvlsconj7ddj3yrjjxydp7ba", "vchh5ha8getigq2rj2hhme5wv", "3asdbsbv1lqq1pjceg4fpshs6", "suplyuf5lt64bv8uqpy5q8spb", "31pitd5ux4a5sf5yriyof4zwuq4a", "312g7lqmmacstibdxxi4qaopn3wa", "31cnzcj7cb7of3tvv36pi5nr4gkm", "31x76k4o5fidt5yvkdyxotav3mdm", "eff4c7i09cr6wpfsrkkjeo1xn", "315ghpwznaaqvegun2qwfzinvk2i", "nfdrk7zus15hxca4byjxvssqk", "rgkn6rysyg1pm3blydjw2qrjm", "31d425fvpofbahnyrj56yb77zrp4", "ecerp6m62k0in7olpcspo794e", "31nftfz6t3k7fszsminocsukyk4q", "31famvvjqzsnaoivyroqtro3cwc4", "31lejcxbwbinhtyflwcn4xrm47iy", "mvz50i4ty9ej5rklwddwyy8l5", "y5hzoh1tkcv3pbbsdz0uz7zld", "31uhinxvoedf7hphgga7wmqlxrqu", "31qlbobbv64srdkuzymnyfctmupa", "frft08bq44mirlwfsbbudiw05", "316iqpoodpwo4tfbavuft2qt77ou", "31e25zo5cg2lf6jmfp6q2fbknd3a", "213hsmcxnqhuxlfbh7dwpm63a", "p9kp5uuovonsk6vu7qovef246", "utm5pcyk8dj3vckzmn3gkvd3h", "315invvrpiw5ecph4sz5spr2mr74", "31gmkgm5n7hawj3ivqta5nmpafeq", "c3uz4rbmmdjyl9yei1p1e2l6n", "g1uq14gl1gkd408usw1oxjrov", "m4q0e720h0s2e1vs1gvwjdywc", "zsaymizci7yi7s5wqjf73qng5", "mx77a9cqqzuw7mcm3nbrrj9yn", "b548de38mk2ut0y5tfj2k4pvo", "31mzw2cinfn5wf3cm3g3db7ipmi4", "31jy4av3x22slmza4g6dhwx3kzz4", "31aje2rvfm265koci2wz66ghwpjm", "31gsgp32blm55uqa7rskjd4frzx4", "fp4ew91e8rg58w2vmcsrz2ini", "31nszrolq5j6inp7kuga3n5nbcfy", "31r5rythissj6nngwbwrfkxmluta", "312xoweqhgascvkyvv5sbhmqp57q", "7lpgt7ox415f5cimzlpnio23e", "312afn4jxuq54zmmkstfrryjzyba", "lg7v1r40dhkkag0ze7r3b4r7c", "31vdnfsmgflsbabzc6j345b4spju", "21tyrd6m4vbxfaoscu3vx4yvy", "ty8z3gzhwy8yqd4mg0600ovua", "5thalr14j490nlk8kjaridu1h", "ru8iowcn9jkc8xg1k9pv74l59", "31onsftvgszddhihuca5hjmjgia4", "31s6mg6orrhnnqeuior4artb3oja", "31xkzvwf2kysi2hfw7iuf4ikp6fu", "21ofvvkw6dr52jjcpucv3fgna", "9q2rheweu4guy193272tsdlym", "31crkllqdtjunntddldfa2gdezeu", "31vm4xpa6heqlj4asjfptgplqi3y", "31tecerevh3t3dv23a7ur4aj6nne", "31codzylmxjlfcyyeapgk6d2zqv4", "pl1bvldkkh8ppccnqe2zyh90j", "316l2434ckw35dbunkzdzj4awxje", "31bbmfouz5ah5g47zokzuzurdsvu", "31jovnsoehcy5gkr254i7mmtqo2m", "31vrvkiey3zzlsvw3adhynak66nq", "31eo57rfkwkx42jsexdfbyoidq2a", "315bnuxm4b3yyqbc43hdvbu2p3fq", "31s7cxqpgvs7mjenpbnftvoq7taq", "rt23u72stdzjmkwzauxz2zfa1", "31f367qafq2avqk3lgoqgswhxesa", "31arkckh6bpjthzd362327ipnj64", "31h56rp76qdqj2ll53zcfkwn2isq", "31nyj4pdtfzuclhvn4dvdpoe6pea", "d1clxy16pvuml76wqyermtpbg", "313ckk33yy2ivmwnjuu6areu4y6u", "9mby3xm5bygkmulihqisforuc", "31tvddv4uoozxhirnimjswnftuci", "31ppaw5easrkwx5rjvtepfib7l7y"]


def init_spotify(client_id, client_secret):
    credentials_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=credentials_manager)


sp = init_spotify(CLIENT_ID, CLIENT_SECRET)

# Connect to SQLite database
conn = sqlite3.connect(DB)
cursor = conn.cursor()

# Load existing IDs from the database


def load_existing_ids(cursor):
    existing_songs = {row[0]
                      for row in cursor.execute('SELECT song_id FROM songs')}
    existing_artists = {row[0] for row in cursor.execute(
        'SELECT artist_id FROM artists')}
    existing_playlists = {row[0] for row in cursor.execute(
        'SELECT playlist_id FROM playlists')}
    return existing_songs, existing_artists, existing_playlists


existing_songs, existing_artists, existing_playlists = load_existing_ids(
    cursor)

# Insert song data into the database


def insert_song(cursor, song_data):
    cursor.execute('''
        INSERT OR REPLACE INTO songs (song_id, song_name, artist_ids, acousticness, danceability, energy,
                                      instrumentalness, key, liveness, loudness, mode, speechiness, tempo,
                                      time_signature, valence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        song_data['song_id'], song_data['song_name'], song_data['artist_ids'],
        song_data['acousticness'], song_data['danceability'], song_data['energy'],
        song_data['instrumentalness'], song_data['key'], song_data['liveness'],
        song_data['loudness'], song_data['mode'], song_data['speechiness'],
        song_data['tempo'], song_data['time_signature'], song_data['valence']
    ))
    existing_songs.add(song_data['song_id'])  # Add to existing_songs set

# Insert artist data into the database


def insert_artist(cursor, artist):
    cursor.execute('''
        INSERT OR REPLACE INTO artists (artist_id, artist_name, artist_genres)
        VALUES (?, ?, ?)
    ''', artist)
    conn.commit()

# Insert playlist data into the database


def insert_playlist(cursor, playlist):
    cursor.execute('''
        INSERT INTO playlists (playlist_id, playlist_creator_id, playlist_original_items, playlist_items)
        VALUES (?, ?, ?, ?)
    ''', playlist)
    conn.commit()

# Update playlist metadata in the database


def update_playlist_metadata(cursor, playlist_id, metadata):
    cursor.execute('''
        UPDATE playlists
        SET playlist_items_fetched = ?,
            playlist_top_artist_ids = ?,
            playlist_top_genres = ?,
            min_acousticness = ?,
            max_acousticness = ?,
            min_danceability = ?,
            max_danceability = ?,
            min_energy = ?,
            max_energy = ?,
            min_instrumentalness = ?,
            max_instrumentalness = ?,
            min_key = ?,
            max_key = ?,
            min_liveness = ?,
            max_liveness = ?,
            min_loudness = ?,
            max_loudness = ?,
            min_mode = ?,
            max_mode = ?,
            min_speechiness = ?,
            max_speechiness = ?,
            min_tempo = ?,
            max_tempo = ?,
            min_time_signature = ?,
            max_time_signature = ?,
            min_valence = ?,
            max_valence = ?
        WHERE playlist_id = ?
    ''', (*metadata, playlist_id))
    conn.commit()

# Scrape Spotify playlist data for a user


def scrape_user_playlists(sp, cursor, user_id):
    try:
        playlists = sp.user_playlists(user_id)

        for playlist in playlists['items']:
            playlist_id = playlist['id']

            if playlist_id in existing_playlists:
                print(f"Skipping playlist {playlist_id} as it already exists.")
                continue

            try:
                playlist_data = sp.playlist(playlist_id)
                playlist_creator_id = playlist_data['owner']['id']
                playlist_items = playlist_data['tracks']['items']

                if len(playlist_items) < 2:
                    print(f"Skipping playlist {
                          playlist_id} because it has fewer than 2 songs.")
                    continue

                track_ids = []
                for item in playlist_items:
                    track = item['track']
                    song_id = track['id']

                    if song_id and song_id not in existing_songs:
                        song_data = extract_song_data(sp, track)
                        if song_data:
                            insert_song(cursor, song_data)

                    track_ids.append(song_id)

                # Insert the playlist data
                insert_playlist(cursor, (playlist_id, playlist_creator_id, len(
                    track_ids), ','.join(track_ids)))
                existing_playlists.add(playlist_id)

            except Exception as e:
                print(f"Error processing playlist {playlist_id}: {e}")

    except Exception as e:
        print(f"Error processing user {user_id}: {e}")

# Extract song data from Spotify API response


def extract_song_data(sp, track):
    try:
        song_id = track['id']
        song_data = {
            'song_id': song_id,
            'song_name': track['name'],
            'artist_ids': ','.join([artist['id'] for artist in track['artists']]),
        }

        # Fetch audio features
        features = sp.audio_features([song_id])[0]
        if features is None:
            return None

        song_data.update({
            'acousticness': features.get('acousticness', 0.0),
            'danceability': features.get('danceability', 0.0),
            'energy': features.get('energy', 0.0),
            'instrumentalness': features.get('instrumentalness', 0.0),
            'key': features.get('key', 0),
            'liveness': features.get('liveness', 0.0),
            'loudness': features.get('loudness', 0.0),
            'mode': features.get('mode', 0),
            'speechiness': features.get('speechiness', 0.0),
            'tempo': features.get('tempo', 0.0),
            'time_signature': features.get('time_signature', 4),
            'valence': features.get('valence', 0.0)
        })
        return song_data
    except Exception as e:
        print(f"Error extracting song data: {e}")
        return None

# Calculate and update playlist metadata in the database


def calculate_and_update_playlist_metadata(cursor, playlist_id):
    cursor.execute(
        'SELECT playlist_items FROM playlists WHERE playlist_id = ?', (playlist_id,))
    result = cursor.fetchone()
    if not result:
        print(f"Playlist {playlist_id} not found in database.")
        return
    song_ids = result[0].split(',')

    # Fetch audio features for all songs in the playlist
    cursor.execute(f'''
        SELECT acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo,
               time_signature, valence, artist_ids
        FROM songs WHERE song_id IN ({','.join(['?'] * len(song_ids))})
    ''', song_ids)
    rows = cursor.fetchall()

    if not rows:
        print(f"No songs found for playlist {playlist_id}.")
        return

    # Initialize min/max variables
    min_acousticness, max_acousticness = float('inf'), float('-inf')
    min_danceability, max_danceability = float('inf'), float('-inf')
    min_energy, max_energy = float('inf'), float('-inf')
    min_instrumentalness, max_instrumentalness = float('inf'), float('-inf')
    min_key, max_key = float('inf'), float('-inf')
    min_liveness, max_liveness = float('inf'), float('-inf')
    min_loudness, max_loudness = float('inf'), float('-inf')
    min_mode, max_mode = float('inf'), float('-inf')
    min_speechiness, max_speechiness = float('inf'), float('-inf')
    min_tempo, max_tempo = float('inf'), float('-inf')
    min_time_signature, max_time_signature = float('inf'), float('-inf')
    min_valence, max_valence = float('inf'), float('-inf')

    # Collect artist and genre information
    artist_counts = {}
    genre_counts = {}

    for row in rows:
        acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence, artist_ids = row

        min_acousticness = min(min_acousticness, acousticness)
        max_acousticness = max(max_acousticness, acousticness)
        min_danceability = min(min_danceability, danceability)
        max_danceability = max(max_danceability, danceability)
        min_energy = min(min_energy, energy)
        max_energy = max(max_energy, energy)
        min_instrumentalness = min(min_instrumentalness, instrumentalness)
        max_instrumentalness = max(max_instrumentalness, instrumentalness)
        min_key = min(min_key, key)
        max_key = max(max_key, key)
        min_liveness = min(min_liveness, liveness)
        max_liveness = max(max_liveness, liveness)
        min_loudness = min(min_loudness, loudness)
        max_loudness = max(max_loudness, loudness)
        min_mode = min(min_mode, mode)
        max_mode = max(max_mode, mode)
        min_speechiness = min(min_speechiness, speechiness)
        max_speechiness = max(max_speechiness, speechiness)
        min_tempo = min(min_tempo, tempo)
        max_tempo = max(max_tempo, tempo)
        min_time_signature = min(min_time_signature, time_signature)
        max_time_signature = max(max_time_signature, time_signature)
        min_valence = min(min_valence, valence)
        max_valence = max(max_valence, valence)

        for artist_id in artist_ids.split(','):
            cursor.execute(
                'SELECT artist_name, artist_genres FROM artists WHERE artist_id = ?', (artist_id,))
            artist = cursor.fetchone()
            if artist:
                artist_name, artist_genres = artist
                artist_counts[artist_name] = artist_counts.get(
                    artist_name, 0) + 1
                for genre in artist_genres.split(','):
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1

    # Get top artists and genres
    top_artists = sorted(
        artist_counts, key=artist_counts.get, reverse=True)[:3]
    top_genres = sorted(genre_counts, key=genre_counts.get, reverse=True)[:3]

    # Update playlist metadata
    metadata = (
        len(song_ids), ','.join(top_artists), ','.join(top_genres),
        min_acousticness, max_acousticness,
        min_danceability, max_danceability,
        min_energy, max_energy,
        min_instrumentalness, max_instrumentalness,
        min_key, max_key,
        min_liveness, max_liveness,
        min_loudness, max_loudness,
        min_mode, max_mode,
        min_speechiness, max_speechiness,
        min_tempo, max_tempo,
        min_time_signature, max_time_signature,
        min_valence, max_valence
    )
    update_playlist_metadata(cursor, playlist_id, metadata)
    conn.commit()

# Main script to scrape data for each user's playlists


def main():
    for user_id in user_ids:
        print(f"Scraping playlists for user {user_id}...")
        scrape_user_playlists(sp, cursor, user_id)
        conn.commit()  # Commit changes after each user's playlists are processed

        # Calculate and update playlist metadata for each scraped playlist
        cursor.execute(
            'SELECT playlist_id FROM playlists WHERE playlist_creator_id = ?', (user_id,))
        for (playlist_id,) in cursor.fetchall():
            calculate_and_update_playlist_metadata(cursor, playlist_id)


if __name__ == '__main__':
    main()

# Close the database connection
conn.close()
