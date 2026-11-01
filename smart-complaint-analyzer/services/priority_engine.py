import re
HIGH = [('exposed electrical wire', 'Exposed electrical wiring poses an immediate safety risk'),('live wire','Potential live electrical hazard'),('open manhole','Open manhole creates a serious injury risk'),('electrocution','Reported electrocution hazard'),('fire outbreak','Reported fire hazard'),('collapsed bridge','Potential structural collapse'),('major road blockage','Major road blockage reported'),('severe water supply disruption','Severe water disruption reported'),('sewage entering homes','Sewage entering homes presents a significant hazard'),('risk of death','Immediate danger to life reported')]
MEDIUM = [('garbage','Waste collection or sanitation concern'),('pothole','Road surface damage needs attention'),('overflow','Overflowing infrastructure needs attention'),('no water','Water service disruption reported'),('broken','Infrastructure repair requested'),('not working','Service or infrastructure fault reported'),('delay','Transport or service delay reported'),('leak','Leak requires inspection')]
def detect_priority(text):
    t = re.sub(r'\s+', ' ', text.lower())
    for phrase,reason in HIGH:
        if phrase in t: return 'High',reason + ' (automated recommendation; human review required)'
    for phrase,reason in MEDIUM:
        if phrase in t: return 'Medium',reason + ' (automated recommendation; human review required)'
    return 'Low','No configured urgent risk indicators found (automated recommendation; human review required)'
