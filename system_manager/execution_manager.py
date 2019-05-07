from system_executor.system_simulator import *
from system_executor.behavior_model_executor import *
from system_manager.es_manager import *

import os
from os import listdir
from os.path import isfile, join

import dill


class ExecutionManager(object):
    def __init__(self, pes_path=".", model_path="."):
        self.pes_db_path = pes_path
        self.model_db_path = model_path
        self.pes_db_map = {}
        self.model_db_map = {}
        self.file_db_init()
        pass

    def file_db_init(self):
        for _file in [f for f in listdir(self.pes_db_path) if isfile(join(self.pes_db_path, f))]:
            self.pes_db_map[_file[:-5]] = os.path.join(os.path.abspath(self.pes_db_path), _file)

        for _file in [f for f in listdir(self.model_db_path) if isfile(join(self.model_db_path, f))]:
            self.model_db_map[_file[:-4]] = os.path.join(os.path.abspath(self.model_db_path), _file)

    @staticmethod
    def sim_menu():
        print("1. List Pruned Entity Structure")
        print("2. Simulation Start")
        print("3. Execute System")
        print("4. Synthesize Executable")
        print("0. Exit")
        return int(input(">>"))

    def _list_pes(self):
        fmt = "{0: <13}\t{1: <13}"
        print(fmt.format("PES Name", "Path"))
        [print(fmt.format(k, v)) for k, v in self.pes_db_map.items()]
        pass

    def _select_pes(self):
        while True:
            self._list_pes()
            selected = input("Select PES:")
            if selected not in self.pes_db_map:
                print("[ERR] Entity Not Found")
            else:
                return EntityManager.static_import_system_entity_structure(self.pes_db_map[selected])

    def _sim_start(self):
        entity_structure = self._select_pes()
        SystemSimulator().register_engine(entity_structure.get_name())
        entities = entity_structure.get_core_attribute().retrieve_entities()
        instance_map = {}
        for entity in entities:
            with open(self.model_db_map[entity[0]], 'rb') as f:
                instance_map[entity[0]] = dill.load(f)
                instance_map[entity[0]].set_engine_name(entity_structure.get_name())
                SystemSimulator().get_engine(entity_structure.get_name()).register_entity(instance_map[entity[0]])

        ic_map = entity_structure.get_core_attribute().retrieve_internal_coupling()
        for model, tup in ic_map.items():
            SystemSimulator().get_engine(entity_structure.get_name()).coupling_relation(
                instance_map[model], tup[0][0], instance_map[tup[0][1][0]], tup[0][1][1])

        SystemSimulator().get_engine(entity_structure.get_name()).simulate()

        pass

    def _sys_exec(self):
        es = self._select_pes()
        SystemSimulator().register_engine(es.get_name())
        attributes = es.get_attribute_list()
        entities = es.get_core_attribute().retrieve_entities()

        ra = None
        for attr in attributes:
            if attr.get_type() == AttributeType.RUNTIME:
                ra = attr

        instance_map = {}
        if not ra:
            for entity in entities:
                with open(self.model_db_map[entity[0]], 'rb') as f:
                    instance_map[entity[0]] = dill.load(f)
                    instance_map[entity[0]].set_engine_name(es.get_name())
                    SystemSimulator().get_engine(es.get_name()).register_entity(instance_map[entity[0]])
        else:
            entity_list = ra.retrieve_entities()
            model_map = ra.retrieve_model_map()
            domain_map = ra.retrieve_domain_map()

            for entity in entity_list:
                with open(model_map[entity], 'rb') as f:
                    instance_map[entity] = dill.load(f)
                with open(domain_map[entity], 'rb') as f:
                    instance_map[entity].domain_obj = dill.load(f)

                instance_map[entity].set_engine_name(es.get_name())
                SystemSimulator().get_engine(es.get_name()).register_entity(instance_map[entity])

        ic_map = es.get_core_attribute().retrieve_internal_coupling()
        for model, tup in ic_map.items():
            SystemSimulator().get_engine(es.get_name()).coupling_relation(
                instance_map[model], tup[0][0], instance_map[tup[0][1][0]], tup[0][1][1])

        SystemSimulator().get_engine(es.get_name()).simulate()

    def _sys_synthesis(self):
        es = self._select_pes()
        SystemSimulator().register_engine(es.get_name())
        attributes = es.get_attribute_list()
        entities = es.get_core_attribute().retrieve_entities()

        ra = None
        for attr in attributes:
            if attr.get_type() == AttributeType.RUNTIME:
                ra = attr

        instance_map = {}
        if not ra:
            for entity in entities:
                with open(self.model_db_map[entity[0]], 'rb') as f:
                    instance_map[entity[0]] = dill.load(f)
                    instance_map[entity[0]].set_engine_name(es.get_name())
                    SystemSimulator().get_engine(es.get_name()).register_entity(instance_map[entity[0]])
        else:
            entity_list = ra.retrieve_entities()
            model_map = ra.retrieve_model_map()
            domain_map = ra.retrieve_domain_map()

            for entity in entity_list:
                with open(model_map[entity], 'rb') as f:
                    instance_map[entity] = dill.load(f)
                if entity in domain_map:
                    with open(domain_map[entity], 'rb') as f:
                        instance_map[entity].domain_obj = dill.load(f)

                instance_map[entity].set_engine_name(es.get_name())
                print(instance_map[entity].get_engine_name())
                SystemSimulator().get_engine(es.get_name()).register_entity(instance_map[entity])

        ic_map = es.get_core_attribute().retrieve_internal_coupling()
        for model, tup in ic_map.items():
            SystemSimulator().get_engine(es.get_name()).coupling_relation(
                instance_map[model], tup[0][0], instance_map[tup[0][1][0]], tup[0][1][1])

        _path = input(">> Enter Path: ")
        with open(os.path.join(os.path.abspath(_path), es.get_name() + ".simx"), 'wb') as f:
            dill.dump(SystemSimulator().get_engine(es.get_name()), f)

    def start(self):
        while True:
            selected = ExecutionManager.sim_menu()

            if selected == 1:
                self._list_pes()
                pass
            elif selected == 2:
                self._sim_start()
                pass
            elif selected == 3:
                self._sys_exec()
                pass
            elif selected == 4:
                self._sys_synthesis()
                pass
            else:
                break
