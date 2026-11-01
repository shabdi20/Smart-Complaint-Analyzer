CATEGORIES = ['Roads and Infrastructure','Sanitation and Garbage','Water Supply','Drainage and Sewage','Electricity and Streetlights','Public Transport','Public Safety','Other']
DEPARTMENTS = ['Public Works Department','Sanitation Department','Water Supply Department','Drainage and Sewerage Department','Electrical Department','Transport Department','Public Safety Department','General Municipal Services']
MAPPING = dict(zip(CATEGORIES, DEPARTMENTS))
def department_for(category): return MAPPING.get(category, MAPPING['Other'])
