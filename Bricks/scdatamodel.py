import pprint
pp = pprint.PrettyPrinter(indent=4, depth=10)
pp.isrecursive(dict)

class SCDataModel():
    
    def __init__(self):
        self.__sc_data = {}


    def __sample_dict_factory(self, sample_details):
        return {'details' : sample_details, 'data_collection_groups' : {}}


    def __dcg_dict_factory(self, parameters):
        return {'parameters' : parameters, 'data_collections' : {}}


    def __dc_dict_factory(self, parameters):
        return {'parameters' : parameters}


    def add_sample(self, key, sample_details):
        self.__sc_data[key] = self.__sample_dict_factory(sample_details)


    def add_data_collection_group(self, sample_key, group_key, parameters):
        self.__sc_data[sample_key]['data_collection_groups'][group_key] = \
            self.__dcg_dict_factory(parameters)


    def add_data_collection(self, sample_key, group_key, 
                            collection_key, parameters):
        self.__sc_data[sample_key]['data_collection_groups'][group_key]\
            ['data_collections'][collection_key] = \
           self. __dc_dict_factory(parameters)


    def remove_data_collection_group(self, sample_key, group_key):
        self.__sc_data[sample_key]['data_collection_groups'].pop(group_key)
        

    def remove_data_collection(self, sample_key, group_key, collection_key):
        self.__sc_data[sample_key]['data_collection_groups'][group_key]\
            ['data_collections'].pop(collection_key)


    def get_data_collection(self, sample_key, group_key, collection_key):
        return self.__sc_data[sample_key]['data_collection_groups'][group_key]\
            ['data_collections'][collection_key]
    

    def __str__(self):
        return pp.pformat(self.__sc_data)

    def __repr__(self):
        return pp.pformat(self.__sc_data)
