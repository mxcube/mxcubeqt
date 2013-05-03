from lxml import etree
import types

FIELD_PROPERTIES = [
    'defaultValue',
    'lowerBound',
    'tooltip',
    'uiClass',
    'uiLabel',
    'unit',
    'upperBound',
    'variableName',
]

def get_field_containers(xml_root):
    if type(xml_root) == types.StringType:
        xml_root = etree.fromstring(xml_root)
    return xml_root.xpath('//object[@class="org.dawb.passerelle.actors.ui.config.FieldContainer"]')

def get_fields(field_container):
    all_fields = list()
    #this is ridiculous
    fields = field_container.xpath('./void[@property="fields"]/void[@method="add"]/object[@class="org.dawb.passerelle.actors.ui.config.FieldBean"]')
    
    for field in fields:
        field_dict = dict()
        #check the field type
        fieldtype = field.xpath('./void[@property="uiClass"]/string')
        if len(fieldtype) == 0:
            fieldtype = 'StandardBox'
        else:
            fieldtype = fieldtype[0].text.strip()

        #try to get the properties according to the type
        if fieldtype.endswith('SpinnerWrapper'):
            field_dict['type'] = 'spinbox'
        if fieldtype.endswith('StandardBox'):
            field_dict['type'] = 'text'
        if fieldtype.endswith('FileBox'):
            field_dict['type'] = 'file'
        if fieldtype.endswith('ComboWrapper'):
            field_dict['type'] = 'combo'

        #get all the other properties
        for prop in FIELD_PROPERTIES:
            p = field.xpath('./void[@property="%s"]/string' % prop)
            if len(p) == 0:
                p = field.xpath('./void[@property="%s"]/double' % prop)
                if len(p) == 0:
                    continue
            #looks like the elem has the prop
            field_dict[prop] = p[0].text.strip()
        
        #special case for the combo: available values
        if field_dict['type'] == 'combo':
            possible_vals = list()
            #please kill me
            vals = field.xpath('./void[@property="textChoices"]/void[@method="add"]/object[@class="org.dawb.passerelle.actors.ui.config.StringValueBean"]/void[@property="textValue"]/string')
            for val in vals:
                possible_vals.append(val.text.strip())
            field_dict['textChoices'] = possible_vals
        
        all_fields.append(field_dict)

    return all_fields

if __name__=='__main__':
    import sys
    f = sys.argv[1]
    doc = etree.parse(f).getroot()
    print '**** containers ****'
    containers = get_field_containers(doc)
    print containers

    for container in containers:
        print '**** fields ****'
        fields = get_fields(container)
        for field in fields:
            print field
    
