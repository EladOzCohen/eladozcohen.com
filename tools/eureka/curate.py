"""Stage 4: turn candidates + YouTube metadata into the final library.

Filters to science / math / AI / ways-of-thinking videos that teach, labels topic, depth and format,
scores by how strongly and how repeatedly Hacker News recommended each one, and applies the hand
overrides in curation.json.   -> ../../static/eureka/videos.json

    python curate.py            build
    python curate.py --report   print what was kept / dropped, for review
"""
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"
OUT = HERE.parent.parent / "static" / "eureka" / "videos.json"
CUR = json.load(open(HERE / "curation.json", encoding="utf-8"))

TOPICS = [
    ("ai", "AI & Machine Learning", "Neural networks, LLMs, reinforcement learning, interpretability, how models actually work"),
    ("math", "Mathematics", "Proofs, structures, and the ideas under everything else"),
    ("stats", "Statistics & Data", "Probability, inference, causality, and reasoning from data"),
    ("physics", "Physics & Cosmos", "From quantum mechanics to the shape of the universe"),
    ("bio", "Life & Mind", "Biology, neuroscience, medicine, cognition"),
    ("cs", "Computer Science", "Algorithms, computation, complexity, cryptography, the theory under software"),
    ("sw", "Software & Systems", "Programming languages, operating systems, databases, distributed systems"),
    ("eng", "Chemistry & Engineering", "Materials, energy, chips and how real things get built"),
    ("mind", "Thinking & Method", "How to learn, do research, reason well and judge evidence"),
]
T = lambda s: re.compile(s, re.I)
TOPIC_RX = {
    "ai": T(r"neural net|deep learning|machine learning|\bAI\b|artificial intell|\bGPT|transformer|\bLLMs?\b|language model|reinforcement learn|backprop|gradient descent|diffusion|attention is|embedding|\bCNNs?\b|convolution|pytorch|tensorflow|alphago|alphafold|alphazero|alignment|interpretab|cs229|cs231n|cs224n|fast\.?ai|\bNLP\b|computer vision|openai|anthropic|deepmind|karpathy|tokeniz|self-driving|autonomous|robotics|\bAGI\b|superintelligen|\bchatgpt|\bclaude\b|scaling law|mechanistic|\bGANs?\b|word2vec|bert\b|\bmodels? (?:learn|train)|training (?:a )?model|generative"),
    "math": T(r"mathemati|calculus|algebra|topolog|geometr|theorem|\bproofs?\b|prime|number theory|eigen|fourier|infinit|combinator|category theory|group theory|manifold|differential equation|real analysis|complex analysis|set theory|g[oö]del|riemann|euler|fractal|chaos|\bpi\b|polynomial|matrix|matrices|vector|dimension|zeta|conjecture|lambda calculus|quaternion|knot|permutation|modular|galois|hilbert"),
    "stats": T(r"statistic|probabilit|bayes|regression|hypothesis|p-value|p value|sampling|causal|data analy|data science|visuali[sz]|variance|confidence interval|monte carlo|markov|time series|a/b test|simpson|randomi[sz]ed|correlation|big data|dataviz|bootstrap|central limit|information theory|entropy"),
    "physics": T(r"physics|quantum|relativity|cosmolog|universe|black hole|particle|string theory|thermodynamic|astronomy|astrophys|gravit|\bspace\b|planet|electromagnet|higgs|dark (?:matter|energy)|big bang|optics|fluid|\bnasa\b|telescope|exoplanet|\bjwst\b|\bligo\b|feynman|lagrangian|hamiltonian|spacetime|photon|electrons?\b|superconduct|laser|nuclear|fusion|solar system|\bstars?\b|galax"),
    "bio": T(r"biolog|neuroscien|\bbrains?\b|\bcells?\b|\bDNA\b|\bgenes?\b|genom|crispr|\bevolution|protein|medicine|medical|cancer|immun|virus|microb|consciousness|cogniti|psycholog|\bsleep|aging|longevity|ecolog|neuron|\bmRNA|vaccine|physiolog|biochem|mitochond|ribosome|enzyme|bacteria|disease|epidemi|pandemic|anatomy|perception|\bmemory\b|organism|species"),
    "cs": T(r"algorithm|data structure|computer architecture|\bcpu\b|type theory|complexity|p vs\.? ?np|cryptograph|turing|computation|\bgpu\b|formal verif|hash|b-tree|blockchain|\bbit(?:s|coin)?\b|encryption|zero.knowledge|quantum comput|computer science|information theory|compression|error.correct|\bboolean|logic gates?|how computers? work|binary"),
    "sw": T(r"programming|software|\bcode\b|coding|compiler|\blisp\b|haskell|\brust\b|golang|\bunix\b|\blinux\b|\bkernel\b|operating system|database|\bsql(?:ite)?\b|distributed|container|docker|kubernetes|\bapi\b|\bjava\b|python|javascript|\bc\+\+|object[- ]oriented|\boops?\b|debugg|refactor|\braft\b|paxos|consensus|concurren|\bthreads?\b|\bgit\b|devops|microservice|\bvm\b|virtual machine|garbage collect|type system|monad|clojure|erlang|scala|\bzig\b|webassembly|user interface|\bvim\b|emacs|functional|interpreter|simple made easy|the mess we"),
    "eng": T(r"chemistry|chemical|molecul|materials?\b|batter(?:y|ies)|engineering|reactor|energy|\bmetal|alloy|steel\b|semiconductor|chip (?:design|fab|making)|lithograph|aerospace|rocket|propulsion|turbine|bridge|structural|circuit|electronics|transistor|manufactur|3d print|power grid|\bpolymer|crystal|catalys|combustion|aerodynamic|rf\b|antenna|signal processing"),
    "mind": T(r"how to learn|learning how to learn|scientific method|critical thinking|\breasoning\b|research (?:taste|career|advice|method)|epistemolog|rational(?:ity|ist)|decision making|mental model|philosophy of science|science communication|peer review|reproducib|replication crisis|cognitive bias|\bexpertise\b|deliberate practice|creativity|thinking (?:fast|clearly|better)|study (?:tips|skills)|you and your research|published research|research (?:wrong|fraud)|scientific (?:fraud|misconduct)|how to speak|public speaking|meta-?science|first principles|problem solving|thinking tools|how to think|learning (?:science|strategies)|\bscience\b.*\b(?:fraud|crisis|trust)"),
}
TOPIC_RX = {k: T(r"\b(?:" + rx.pattern + ")") for k, rx in TOPIC_RX.items()}  # word-start match: "Steele" is not "steel"
# YouTube categories that are almost never teaching content
BAD_CAT = {"Music", "Comedy", "Gaming", "Sports", "Autos & Vehicles", "Pets & Animals", "Travel & Events", "Entertainment",
           "Film & Animation", "Howto & Style", "Shows", "Trailers", "Movies", "News & Politics", "Nonprofits & Activism"}
# titles that are entertainment/news/opinion, whatever the channel
BAD_TITLE = T(r"official (?:music )?video|\bmusic video\b|\btrailer\b|\breact(?:s|ion)\b|\bfunny\b|\bprank\b|\bepisode \d+\b.*\bpodcast\b|\bvlog\b|\bunboxing\b|\bgameplay\b|\bwalkthrough\b|\bhighlights\b|\bfull movie\b|\bsnl\b|\bstand-?up\b|\bdebate\b|\bpresident\b|\belection\b|\bcongress\b|\bsenate\b|\btrump\b|\bbiden\b|\bobama\b|\bwar in\b|\bukraine\b|\bgaza\b|commencement|\bmarvel\b|simpsons|bootstrapped|crises small|killer arms|starcraft|parrots, the universe|24/7|gold dig|vaccine mandate|senior rust developer|raise money|blitzscaling|webpack|synthesizer")
SPARK_CH = T(r"^(?:kurzgesagt|vsauce\d?|veritasium|smarter ?every ?day|mark rober|ted|ted-ed|tedx.*|big think|wired|vice|vox|national geographic|discovery|history|history channel|cnbc|bloomberg.*|cheddar|coldfusion|nerdwriter1|wendover productions|minutephysics|physics girl|scishow.*|be smart|joe scott|real engineering|tom scott|vsauce.*|numberphile2?|the infographics show|simple ?history|knowing better|veritasium|the royal institution|2veritasium|colin and samir|youtube originals|dw documentary|bbc.*|pbs.*(?:eons|infinite series)?|nova pbs official|up and atom|dr\.? ?becky|sabine hossenfelder|anton petrov|sixty symbols|brady haran|periodic videos|ted talks?)$")
SPARK_TITLE = T(r"mind[- ]?blowing|you won'?t believe|shocking|\btop \d+\b|^\d+ (?:facts|things|ways|reasons)|will change (?:your|the) |everything you need to know|in (?:\d+|one|a few) minutes?|\bexplained\b.*\bsimply\b|\bfor beginners\b.*\bin \d+|secrets? (?:of|behind)|the truth about|the (?:insane|crazy|mind)|\bwhy (?:everything|nothing) you\b|\bwill (?:blow|shock)|\bstrange\b.*\bworld\b")
LECTURE_CH = T(r"mit |opencourseware|stanford|yale|harvard|berkeley|caltech|carnegie|oxford|cambridge|princeton|columbia|cornell|\buniversity\b|university of|institute for advanced|simons institute|perimeter institute|\bicml\b|neurips|\biclr\b|\bcvpr\b|deepmind|openai|anthropic|\bcern\b|santa fe institute|\bcs50\b|\bnptel\b|\bcoursera\b|\bedx\b|\bcmu\b|epfl|eth z|\btu delft|weizmann|\bbroad institute|\bhhmi\b|allen institute|\bkitp\b|\bicts\b|securitylectures")
LECTURE_TITLE = T(r"lecture\s*#?\d+|\blec\.? ?\d+|\bcs ?\d{2,3}[a-z]?\b|\bmit \d[\.\d]+|\b\d{1,2}\.\d{3}\b|\bfull course\b|\bcourse\b|\bsyllabus\b|\bclass \d+|\bseminar\b|\bcolloquium\b|\bkeynote\b|\bopen ?courseware\b|\blecture\b|\bsession \d+")
BUILD_TITLE = T(r"from scratch|let'?s (?:build|reproduce|code)|\bimplement|building (?:a|an|the)\b|step[- ]by[- ]step|\bcode[- ]along|\bhands[- ]on\b|\bzero to hero\b|\bwalk-?through\b.*\bcode|\bin (?:python|pytorch|numpy|c\+\+|rust|julia)\b")
DEEP_TITLE = T(r"derivation|\bproof\b|deep dive|in depth|in-depth|\bmasterclass\b|first principles|mathematics of|math(?:s)? behind|how (?:it|they) (?:really )?works?|under the hood|internals|paper (?:explained|walkthrough)|\barxiv\b|visual(?:ly)? (?:explained|guide)|a (?:gentle|visual|friendly) introduction|\bexplained\b|\bintuition\b|the (?:math|physics|science) of")
INTERVIEW_TITLE = T(r"\binterview\b|\bconversation\b|\bpodcast\b|\bin conversation\b|\bwith (?:dr\.?|prof)|\bq ?& ?a\b|\bpanel\b|\bfireside\b")
DOC_TITLE = T(r"documentary|\bfull film\b|\bdoc\b")
TALK_TITLE = T(r"\btalk\b|\bkeynote\b|\bpresentation\b|\bconference\b|\bsummit\b|\bworkshop\b|\bsymposium\b")
HIGH_TRUST_CH = T(r"^(?:3blue1brown|andrej karpathy|welch labs|statquest.*|computerphile|mutual information|neel nanda|yannic kilcher|two minute papers|sean carroll|stanford online|mit opencourseware|mit csail|the royal institution|numberphile|pbs space time|pbs infinite series|stephen wolfram|lex fridman|machine learning street talk|jeremy howard|ai explained|sentdex|artem kirsanov|looking glass universe|3blue1brown.*|brian greene|professor leonard|eigenchris|mathologer|zach star|physics explained|david silver|deeplearning\.ai|google deepmind|openai|anthropic|andrew ng|the coding train|computer science|steve brunton|vsauce)$")


def theme_scores(text_t, text_c, text_d, text_h):
    out = {}
    for k, rx in TOPIC_RX.items():
        s = 3 * len(rx.findall(text_t)) + 2 * len(rx.findall(text_c)) + 1 * len(rx.findall(text_d)) + 0.3 * len(rx.findall(text_h))
        if s:
            out[k] = s
    return out


def classify(m, hn):
    title, ch, desc = m["title"] or "", m["ch"] or "", (m["desc"] or "")[:450]
    h = " ".join(([hn["sub"]] if hn["sub"] else []) + hn["ctx"])
    sc = theme_scores(title, ch, desc, h)
    # title evidence outweighs thread-title noise
    tp = max(sc, key=sc.get) if sc else None
    strength = sc.get(tp, 0) if tp else 0
    return tp, strength, sc


def depth_format(m, tp):
    title, ch, desc = m["title"], m["ch"] or "", (m["desc"] or "")[:350]
    mins = m["len"] / 60
    dp = 2
    if LECTURE_TITLE.search(title) or LECTURE_CH.search(ch):
        dp = 4 if mins >= 25 else 3
    if BUILD_TITLE.search(title) and mins >= 25:
        dp = max(dp, 3)
    if DEEP_TITLE.search(title) and mins >= 20:
        dp = max(dp, 3)
    if mins >= 75 and dp == 2:
        dp = 3
    if SPARK_CH.search(ch) or SPARK_TITLE.search(title):
        dp = 1 if not (LECTURE_TITLE.search(title) and mins >= 40) else dp
    if DOC_TITLE.search(title) or "documentary" in desc.lower()[:120]:
        dp = 1  # documentaries inspire; they rarely teach the mechanics
    if mins < 12 and dp > 2:
        dp = 2
    if mins < 9:
        dp = min(dp, 2)
    fm = ("lecture" if LECTURE_TITLE.search(title) and mins >= 25 else "build" if BUILD_TITLE.search(title) else
          "interview" if INTERVIEW_TITLE.search(title + " " + ch) else "doc" if DOC_TITLE.search(title) else
          "talk" if TALK_TITLE.search(title) or mins >= 25 and dp >= 3 else "explainer")
    return dp, fm


def main():
    cands = {r["v"]: r for r in json.load(open(DATA / "candidates.json", encoding="utf-8"))}
    meta = {}
    shortlist = "--shortlist" in sys.argv
    if shortlist:  # first pass: only title + channel known, so judge by those and keep unknown fields neutral
        for line in open(DATA / "oembed.jsonl", encoding="utf-8"):
            r = json.loads(line)
            meta[r["v"]] = dict(v=r["v"], status="OK" if r["code"] == 200 else "GONE", embed=True, title=r.get("title"),
                                ch=r.get("ch"), len=1800, views=0, date="", cat=None, desc="")
    else:
        for line in open(DATA / "meta.jsonl", encoding="utf-8"):
            r = json.loads(line)
            meta[r["v"]] = r
    allow_ch, block_ch = CUR.get("allow_channels", []), CUR.get("block_channels", [])
    block_ids, allow_ids = set(CUR.get("block_ids", [])), set(CUR.get("allow_ids", []))
    topic_over = CUR.get("topic_override", {})
    dp_over = CUR.get("depth_override", {})
    ch_dp = CUR.get("channel_depth", {})
    ch_tp = CUR.get("channel_topic", {})
    ch_def = CUR.get("channel_default", {})
    pre = lambda ch, keys: any((ch or "").lower() == k[1:].lower() if k.startswith("=") else (ch or "").lower().startswith(k.lower()) for k in keys)
    look = lambda ch, mp: next((val for k, val in mp.items() if (ch or "").lower().startswith(k.lower())), None)
    why = Counter()
    kept = []
    dropped = defaultdict(list)
    for v, m in meta.items():
        hn = cands.get(v)
        if not hn:
            continue

        def drop(reason):
            why[reason] += 1
            dropped[reason].append(v)

        if m["status"] != "OK" or not m.get("title"):
            drop("unavailable"); continue
        if not m.get("embed"):
            drop("no-embed"); continue
        if v in block_ids or pre(m["ch"], block_ch):
            drop("blocked"); continue
        forced = v in allow_ids or pre(m["ch"], allow_ch) or bool(hn.get("mine"))
        if m["len"] < (180 if forced else 420):  # even trusted channels: a 1-minute clip does not teach
            drop("too-short"); continue
        if BAD_TITLE.search(m["title"]) or (m.get("cat") in BAD_CAT and not forced):
            drop("off-category"); continue
        tp, strength, sc = classify(m, hn)
        dflt = look(m["ch"], ch_def)  # single-subject channels: weak keyword evidence loses to the channel's home topic
        tp = topic_over.get(v) or look(m["ch"], ch_tp) or (dflt if dflt and strength < 6 else None) or tp or (dflt if forced else None)
        if tp is None:
            drop("no-topic"); continue
        title_hit = theme_scores(m["title"], m["ch"] or "", "", "").get(tp, 0)
        desc_hit = len(TOPIC_RX[tp].findall(m["desc"] or ""))
        # only two recommenders: trust hand-vetted channels, and the topics HN rarely covers (stats, thinking, life sciences)
        if hn["au"] < 3 and hn["pts"] < 100 and not forced and not (tp in ("stats", "mind", "bio") and title_hit > 0):
            drop("low-signal"); continue
        if not forced and not (v in topic_over or look(m["ch"], ch_tp)):
            if shortlist and strength < 3 and title_hit == 0:
                drop("weak-topic"); continue
            if not shortlist and title_hit == 0 and desc_hit < 2:
                drop("weak-topic"); continue
        dp, fm = depth_format(m, tp)
        dp = dp_over.get(v, look(m["ch"], ch_dp) or dp)
        year = int(m["date"][:4]) if m["date"] else hn["y0"]
        span = hn["y1"] - hn["y0"]
        raw = (0.50 * math.log1p(hn["au"]) / math.log1p(40) + 0.14 * min(span, 10) / 10 + 0.10 * min(hn["rec"], 12) / 12
               + 0.08 * math.log1p(hn["pts"]) / math.log1p(1500) + 0.04 * (dp - 1) / 3 + (0.45 if hn.get("mine") else 0))
        kept.append(dict(
            id=v, t=m["title"], c=m["ch"], l=m["len"], y=year, vw=m["views"], tp=tp, dp=dp, fm=fm,
            au=hn["au"], n=hn["n"], y0=hn["y0"], y1=hn["y1"], rec=hn["rec"], sc=round(min(raw, 1.0), 4),
            th=hn["th"], tt=hn["tt"],
            _desc=m["desc"], _tpscore=round(strength, 1)))
    print("meta rows", len(meta), "| kept", len(kept))
    print("dropped:", dict(why))
    print("topics:", dict(Counter(k["tp"] for k in kept)))
    print("depth:", dict(Counter(k["dp"] for k in kept)))
    if shortlist:
        ids = {k["id"] for k in kept}
        json.dump([cands[v] for v in cands if v in ids], open(DATA / "shortlist.json", "w", encoding="utf-8"), ensure_ascii=False)
        print("shortlist:", len(ids), "-> data/shortlist.json")
        return
    if "--report" in sys.argv:
        json.dump({"kept": kept, "dropped": dropped}, open(DATA / "report.json", "w", encoding="utf-8"), ensure_ascii=False)
        return
    for k in kept:
        k.pop("_desc"); k.pop("_tpscore")
    kept.sort(key=lambda k: -k["sc"])
    out = dict(meta=dict(built=date.today().isoformat(), count=len(kept),
                         topics=[dict(id=i, name=n, desc=d) for i, n, d in TOPICS]), v=kept)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("wrote", OUT, f"{OUT.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
