from system_manager.system_manager import *
import os


class telegram_entityManager:
    def __init__(self):
        self.operation_count = 0
        self.glob_lst = {}
        self.entity_path = "./sample/ses_db"
        self.sm = SystemManager("./sample/ses_db", "./sample/model_db", './sample/pes_db')
        self.entity_db = []
        self.model_db = {}
        self.make_db()

        self.selected = ""
        self.char_memo_1 = ""
        self.char_memo_2 = ""
        self.char_memo_3 = ""
        self.char_memo_4 = ""
        self.char_memo_5 = ""
        self.int_memo = 0
        self.list_memo = []
        self.list_memo_2 = []

        self.esm = None
        self.entity = None
        self.aft_msa = None

        self.pes = None
        self.ra = None
    def make_db(self):
        self. entity_db = [f for f in listdir(self.entity_path) if isfile(join(self.entity_path, f))]
        for _file in self.entity_db:
            self.model_db[_file[:-5]] = os.path.join(os.path.abspath(self.entity_path), _file)

    def clear_system(self):
        self.glob_lst = {}
        self.operation_count = 0
        self.selected = ""
        self.clear_memo()

    def clear_memo(self):
        self.char_memo_1 = ""
        self.char_memo_2 = ""
        self.char_memo_3 = ""
        self.char_memo_4 = ""
        self.char_memo_5 = ""
        self.int_memo = 0
        self.list_memo = []
        self.list_memo_2 = []

    def load_entity(self, selected):
        self.esm = EntityManager()
        self.entity = self.esm.create_entity_structure()

        json_data = open(self.model_db[selected]).read()
        data = json.loads(json_data)
        self.aft_msa = ModelStructuralAttribute()
        self.entity.set_name(selected)
        core = data["core_attribute"]
        for ntnm, arti, opt in core["entities"]:
            self.aft_msa.insert_entity(ntnm, arti, opt)
        self.aft_msa.input_ports = core["input_ports"]
        self.aft_msa.output_ports = core["output_ports"]
        self.aft_msa.external_input_map = core["external_input"]
        self.aft_msa.external_output_map = core["external_output"]
        self.aft_msa.internal_coupling_map_entity = core["internal"]
        map_tuple = {}
        for key, item in core["internal"].items():
            in_lst = []
            for inoutlst in item:
                out_tpl = (key, inoutlst[0])
                in_tpl = (inoutlst[1][0], inoutlst[1][1])
                in_lst.append(in_tpl)
                map_tuple[out_tpl] = in_lst
        self.aft_msa.internal_coupling_map_tuple = map_tuple

    def save_entity(self):
        esm = EntityManager()
        entity = esm.create_entity_structure()
        entity.set_core_attribute(self.aft_msa)
        esm.create_system(entity)
        esm.export_system_entity_structure(entity, self.entity_path, self.selected + ".json")

    def YN_again_menu(self, update, restart_num):
        if update.message.text == "y":
            self.operation_count -= restart_num
            return False
        elif update.message.text == "n":
            self.operation_count += 1
            return True
        else:
            update.message.reply_text("please type only y or n")
            return False

    def YN_nextstep_menu(self, update, nextstep_num):
        if update.message.text == "y":
            self.operation_count += 1
            return True
        elif update.message.text == "n":
            self.operation_count += nextstep_num
            return False
        else:
            update.message.reply_text("please type only y or n")
            return False

    def Chk_int(self, update, _num):
        try:
            int(_num)
            return True
        except ValueError:
            update.message.reply_text("please type int")
            return False

    def print_entity_db(self,update):
        fmt = "{0: <13}\t{1: <13}"
        st = ""
        for k, v in self.model_db.items():
            st += fmt.format(k, v) + "\n"
        update.message.reply_text(st)

    def print_entity_information(self, update, target):
        fmt = "{0: <10}{name: <15}\t{arity: <5}\t{opt: <5}"
        _str = ""
        _str += "Name: " + target.entity_name + "\n"
        _str += fmt.format("Entities: ", name="Name", arity="Arity", opt="Optional") + "\n"
        entities = target.core_attribute.retrieve_entities()

        for idx, entity in enumerate(entities):
            _str += "\t" + fmt.format(idx+1, name=entity[0], arity=entity[1], opt=entity[2]) + "\n"

        update.message.reply_text(_str)

    def print_port_information(self, update, target):
        _str = ""
        _str += "Name: " + target.entity_name + "\n"

        print("input port: ", self.aft_msa.input_ports)
        print("output port: ", self.aft_msa.output_ports)
        print("external input: ", self.aft_msa.external_input_map)
        print("external output: ", self.aft_msa.external_output_map)
        print("internal: ", self.aft_msa.internal_coupling_map_entity)
        print("internal: ", self.aft_msa.internal_coupling_map_tuple)

        _str += "<Input port>" + "\n"
        _str += str(self.aft_msa.input_ports) + "\n"
        _str += "<Output port>" + "\n"
        _str += str(self.aft_msa.output_ports) + "\n"
        _str += "<External Input>" + "\n"
        _str += str(self.aft_msa.external_input_map) + "\n"
        _str += "<External Output>" + "\n"
        _str += str(self.aft_msa.external_output_map) + "\n"
        _str += "<Internal>"+ "\n"
        _str += str(self.aft_msa.internal_coupling_map_tuple)

        update.message.reply_text(_str)

    def create_option(self, update):
        if self.operation_count == 0:
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
            return
        elif self.operation_count == 1:
            self.glob_lst["name"] = update.message.text
            update.message.reply_text("How many input port did system need")
            self.operation_count += 1

        elif self.operation_count == 2:
            if self.Chk_int(update, update.message.text):
                self.glob_lst["num_input_port"] = update.message.text
                update.message.reply_text("How many output port did system need")
                self.operation_count += 1

        elif self.operation_count == 3:
            if self.Chk_int(update, update.message.text):
                self.glob_lst["num_output_port"] = update.message.text
                update.message.reply_text("What is the entity name?")
                self.operation_count += 1

        elif self.operation_count == 4:
            if "entities name" in self.glob_lst.keys():
                self.glob_lst["entities name"].append(update.message.text)
            else:
                self.glob_lst["entities name"] = [update.message.text]
            update.message.reply_text("Type number of arity")
            self.operation_count += 1

        elif self.operation_count == 5:
            if self.Chk_int(update, update.message.text):
                if "attribute number" in self.glob_lst.keys():
                    self.glob_lst["attribute number"].append(update.message.text)
                else:
                    self.glob_lst["attribute number"] = [update.message.text]
                update.message.reply_text("is this entity optional? (y/n)")
                self.operation_count += 1

        elif self.operation_count == 6:
            if update.message.text == "y":
                self.operation_count += 1
                if "optional" in self.glob_lst.keys():
                    self.glob_lst["optional"].append(True)
                else:
                    self.glob_lst["optional"] = [True]
                update.message.reply_text("Did you need more entity? (y/n)")
            elif update.message.text == "n":
                self.operation_count += 1
                if "optional" in self.glob_lst.keys():
                    self.glob_lst["optional"].append(False)
                else:
                    self.glob_lst["optional"] = [False]
                update.message.reply_text("Did you need more entity? (y/n)")
            else:
                update.message.reply_text("please type only y or n")

        elif self.operation_count == 7:
            print(self.glob_lst)
            if self.YN_again_menu(update, 3):
                update.message.reply_text("did you want to make external input port? (y/n)")
            else:
                if update.message.text == "y":
                    update.message.reply_text("What is the entity name?")

        elif self.operation_count == 8:
            if self.YN_nextstep_menu(update, 5):
                update.message.reply_text("number of input port :" + self.glob_lst["num_input_port"])
                update.message.reply_text("type the 'number' of input port that you will use for external input port")
            else:
                if update.message.text == "n":
                    update.message.reply_text("did you want to make external output port? (y/n)")

        elif self.operation_count == 9:
            if self.Chk_int(update, update.message.text):
                if float(update.message.text) <= float(self.glob_lst["num_input_port"]):
                    port_num = "in"+ update.message.text
                    if "ex_in_portnum" in self.glob_lst.keys():
                        self.glob_lst["ex_in_portnum"].append(port_num)
                    else:
                        self.glob_lst["ex_in_portnum"] = [port_num]
                    self.operation_count += 1
                    update.message.reply_text("created entities: " + str(self.glob_lst["entities name"]))
                    update.message.reply_text("choose entity to connect with input port")
                else:
                    update.message.reply_text("please type again")

        elif self.operation_count == 10:
            if update.message.text in self.glob_lst["entities name"]:
                if "ex_in_entity" in self.glob_lst.keys():
                    self.glob_lst["ex_in_entity"].append(update.message.text)
                else:
                    self.glob_lst["ex_in_entity"] = [update.message.text]
                update.message.reply_text("number of input port :" + self.glob_lst["num_input_port"])
                update.message.reply_text(
                    "Type the 'number' of input port that you will use for " + update.message.text + " input port")
                self.operation_count += 1
            else:
                update.message.reply_text("please type name that you create")

        elif self.operation_count == 11:
            if self.Chk_int(update, update.message.text):
                if float(update.message.text) <= float(self.glob_lst["num_input_port"]):
                    port_num = "in" + update.message.text
                    if "ex_in_portenti" in self.glob_lst.keys():
                        self.glob_lst["ex_in_portenti"].append(port_num)
                    else:
                        self.glob_lst["ex_in_portenti"] = [port_num]
                    self.operation_count += 1
                    update.message.reply_text("did you need more connection? (y/n)")
                else:
                    update.message.reply_text("please type again")

        elif self.operation_count == 12:
            print(self.glob_lst)
            if self.YN_again_menu(update, 3):
                update.message.reply_text("did you want to make external output port? (y/n)")
            else:
                if update.message.text == "y":
                    update.message.reply_text("number of input port :" + str(self.glob_lst["num_input_port"]))
                    update.message.reply_text(
                        "type the 'number' of input port that you will use for external input port")

        elif self.operation_count == 13:
            if self.YN_nextstep_menu(update, 5):
                update.message.reply_text("number of output port :" + str(self.glob_lst["num_output_port"]))
                update.message.reply_text("type the 'number' of output port that you will use for external output port")
            else:
                if update.message.text == "n":
                    update.message.reply_text("did you want to make internal port? (y/n)")

        elif self.operation_count == 14:
            if self.Chk_int(update, update.message.text):
                if float(update.message.text) <= float(self.glob_lst["num_output_port"]):
                    port_num = "out" + update.message.text
                    if "ex_out_portnum" in self.glob_lst.keys():
                        self.glob_lst["ex_out_portnum"].append(port_num)
                    else:
                        self.glob_lst["ex_out_portnum"] = [port_num]
                    self.operation_count += 1
                    update.message.reply_text("created entities: " + str(self.glob_lst["entities name"]))
                    update.message.reply_text("choose entity to connect with output port")
                else:
                    update.message.reply_text("please type again")

        elif self.operation_count == 15:
            if update.message.text in self.glob_lst["entities name"]:
                if "ex_out_entity" in self.glob_lst.keys():
                    self.glob_lst["ex_out_entity"].append(update.message.text)
                else:
                    self.glob_lst["ex_out_entity"] = [update.message.text]
                update.message.reply_text("number of output port :" + str(self.glob_lst["num_output_port"]))
                update.message.reply_text(
                    "Type the 'number' of output port that you will use for " + update.message.text + " output port")
                self.operation_count += 1
            else:
                update.message.reply_text("please type name that you create")

        elif self.operation_count == 16:
            if self.Chk_int(update, update.message.text):
                if float(update.message.text) <= float(self.glob_lst["num_output_port"]):
                    port_num = "out" + update.message.text
                    if "ex_out_portenti" in self.glob_lst.keys():
                        self.glob_lst["ex_out_portenti"].append(port_num)
                    else:
                        self.glob_lst["ex_out_portenti"] = [port_num]
                    self.operation_count += 1
                    update.message.reply_text("did you need more connection? (y/n)")
                else:
                    update.message.reply_text("please type again")

        elif self.operation_count == 17:
            print(self.glob_lst)
            if self.YN_again_menu(update, 3):
                update.message.reply_text("did you want to make internal port? (y/n)")
            else:
                if update.message.text == "y":
                    update.message.reply_text("number of output port :" + str(self.glob_lst["num_output_port"]))
                    update.message.reply_text(
                        "type the 'number' of output port that you will use for external output port")

        elif self.operation_count == 18:
            if self.YN_nextstep_menu(update, 5):
                update.message.reply_text("created entities: " + str(self.glob_lst["entities name"]))
                update.message.reply_text("choose first entity out to other")
            else:
                if update.message.text == "n":
                    esm = EntityManager()
                    msa = ModelStructuralAttribute()
                    entity = esm.create_entity_structure()
                    entity.set_name(self.glob_lst["name"])
                    if int(self.glob_lst["num_input_port"]) > 0:
                        for i in range(int(self.glob_lst["num_input_port"])):
                            nm = "in" + str(i + 1)
                            msa.insert_input_port(nm)
                    if int(self.glob_lst["num_output_port"]) > 0:
                        for i in range(int(self.glob_lst["num_output_port"])):
                            nm = "out" + str(i + 1)
                            msa.insert_output_port(nm)
                    for i in range(len(self.glob_lst["entities name"])):
                        msa.insert_entity(self.glob_lst["entities name"][i], self.glob_lst["attribute number"][i],
                                          self.glob_lst["optional"][i])
                    if self.glob_lst.get("ex_in_portnum") is not None:
                        for i in range(len(self.glob_lst["ex_in_portnum"])):
                            msa.insert_coupling(("", self.glob_lst["ex_in_portnum"][i]),
                                                (self.glob_lst["ex_in_entity"][i],
                                                 self.glob_lst["ex_in_portenti"][i]))
                    if self.glob_lst.get("ex_out_portnum") is not None:
                        for i in range(len(self.glob_lst["ex_out_portnum"])):
                            msa.insert_coupling(
                                (self.glob_lst["ex_out_entity"][i], self.glob_lst["ex_out_portenti"][i]),
                                ("", self.glob_lst["ex_out_portnum"][i]))
                    if self.glob_lst.get("internal_out_entity") is not None:
                        for i in range(len(self.glob_lst["internal_out_entity"])):
                            msa.insert_coupling((self.glob_lst["internal_out_entity"][i],
                                                 self.glob_lst["internal_out_port"][i]),
                                                (self.glob_lst["internal_in_entity"][i],
                                                 self.glob_lst["internal_in_port"][i]))
                    entity.set_core_attribute(msa)
                    esm.create_system(entity)
                    esm.export_system_entity_structure(entity, self.entity_path, str(self.glob_lst["name"]) + ".json")

                    self.clear_system()
        elif self.operation_count == 19:
            if update.message.text in self.glob_lst["entities name"]:
                if "internal_out_entity" in self.glob_lst.keys():
                    self.glob_lst["internal_out_entity"].append(update.message.text)
                else:
                    self.glob_lst["internal_out_entity"] = [update.message.text]
                update.message.reply_text("number of output port :" + str(self.glob_lst["num_output_port"]))
                update.message.reply_text(
                    "Type the 'number' of output port that you will use for " + update.message.text + " output port")
                self.operation_count += 1
            else:
                update.message.reply_text("please type name that you create")
        elif self.operation_count == 20:
            if self.Chk_int(update, update.message.text):
                if float(update.message.text) <= float(self.glob_lst["num_output_port"]):
                    port_num = "out" + update.message.text
                    if "internal_out_port" in self.glob_lst.keys():
                        self.glob_lst["internal_out_port"].append(port_num)
                    else:
                        self.glob_lst["internal_out_port"] = [port_num]
                    self.operation_count += 1
                    update.message.reply_text("created entities: " + str(self.glob_lst["entities name"]))
                    update.message.reply_text("choose second entity in by other")
                else:
                    update.message.reply_text("please type again")
        elif self.operation_count == 21:
            if update.message.text in self.glob_lst["entities name"]:
                if "internal_in_entity" in self.glob_lst.keys():
                    self.glob_lst["internal_in_entity"].append(update.message.text)
                else:
                    self.glob_lst["internal_in_entity"] = [update.message.text]
                update.message.reply_text("number of input port :" + str(self.glob_lst["num_input_port"]))
                update.message.reply_text(
                    "Type the 'number' of input port that you will use for " + update.message.text + " input port")
                self.operation_count += 1
            else:
                update.message.reply_text("please type name that you create")
        elif self.operation_count == 22:
            if self.Chk_int(update, update.message.text):
                if float(update.message.text) <= float(self.glob_lst["num_input_port"]):
                    port_num = "in" + update.message.text
                    if "internal_in_port" in self.glob_lst.keys():
                        self.glob_lst["internal_in_port"].append(port_num)
                    else:
                        self.glob_lst["internal_in_port"] = [port_num]
                    self.operation_count += 1
                    update.message.reply_text("Did you need more connection? (y/n)")
                else:
                    update.message.reply_text("please type again")

        elif self.operation_count == 23:
            if self.YN_again_menu(update, 4):
                esm = EntityManager()
                msa = ModelStructuralAttribute()
                entity = esm.create_entity_structure()
                entity.set_name(self.glob_lst["name"])
                if int(self.glob_lst["num_input_port"]) >0:
                    for i in range(int(self.glob_lst["num_input_port"])):
                        nm = "in"+str(i+1)
                        msa.insert_input_port(nm)
                if int(self.glob_lst["num_output_port"]) > 0:
                    for i in range(int(self.glob_lst["num_output_port"])):
                        nm = "out"+str(i+1)
                        msa.insert_output_port(nm)
                for i in range(len(self.glob_lst["entities name"])):
                    msa.insert_entity(self.glob_lst["entities name"][i], self.glob_lst["attribute number"][i],
                                      self.glob_lst["optional"][i])
                if self.glob_lst.get("ex_in_portnum") is not None:
                    for i in range(len(self.glob_lst["ex_in_portnum"])):
                        msa.insert_coupling(("", self.glob_lst["ex_in_portnum"][i]), (self.glob_lst["ex_in_entity"][i],
                                                                                      self.glob_lst["ex_in_portenti"][i]))
                if self.glob_lst.get("ex_out_portnum") is not None:
                    for i in range(len(self.glob_lst["ex_out_portnum"])):
                        msa.insert_coupling((self.glob_lst["ex_out_entity"][i], self.glob_lst["ex_out_portenti"][i]),
                                            ("", self.glob_lst["ex_out_portnum"][i]))
                if self.glob_lst.get("internal_out_entity") is not None:
                    for i in range(len(self.glob_lst["internal_out_entity"])):
                        msa.insert_coupling((self.glob_lst["internal_out_entity"][i],
                                             self.glob_lst["internal_out_port"][i]),
                                            (self.glob_lst["internal_in_entity"][i],
                                             self.glob_lst["internal_in_port"][i]))
                entity.set_core_attribute(msa)
                esm.create_system(entity)
                esm.export_system_entity_structure(entity, self.entity_path, str(self.glob_lst["name"]) + ".json")

                self.clear_system()

            else:
                if update.message.text == "y":
                    update.message.reply_text("created entities: " + str(self.glob_lst["entities name"]))
                    update.message.reply_text("choose first entity out to other")

    def read_option(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                model = self.sm.esm.import_system_entity_structure(self.model_db[update.message.text])
                print(model)
                self.print_entity_information(update, model)
                self.clear_system()
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")

    def update_option_addenti(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                self.load_entity(self.selected)
                self.print_entity_information(update, model)
                update.message.reply_text("Type the entity name you will create")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            if "entities name" in self.glob_lst.keys():
                self.glob_lst["entities name"].append(update.message.text)
            else:
                self.glob_lst["entities name"] = [update.message.text]
            update.message.reply_text("Type number of arity")
            self.operation_count += 1

        elif self.operation_count == 3:
            if self.Chk_int(update, update.message.text):
                if "attribute number" in self.glob_lst.keys():
                    self.glob_lst["attribute number"].append(update.message.text)
                else:
                    self.glob_lst["attribute number"] = [update.message.text]
                update.message.reply_text("is this entity optional? (y/n)")
                self.operation_count += 1

        elif self.operation_count == 4:
            if update.message.text == "y":
                self.operation_count += 1
                if "optional" in self.glob_lst.keys():
                    self.glob_lst["optional"].append(True)
                else:
                    self.glob_lst["optional"] = [True]
                update.message.reply_text("Did you need more entity? (y/n)")
            elif update.message.text == "n":
                self.operation_count += 1
                if "optional" in self.glob_lst.keys():
                    self.glob_lst["optional"].append(False)
                else:
                    self.glob_lst["optional"] = [False]
                update.message.reply_text("Did you need more entity? (y/n)")
            else:
                update.message.reply_text("please type only y or n")

        elif self.operation_count == 5:
            print(self.glob_lst)
            if self.YN_again_menu(update, 3):
                for i in range(len(self.glob_lst["entities name"])):
                    self.aft_msa.insert_entity(self.glob_lst["entities name"][i],
                                               self.glob_lst["attribute number"][i],
                                               self.glob_lst["optional"][i])
                self.save_entity()
                self.clear_system()

            else:
                if update.message.text == "y":
                    update.message.reply_text("What is the entity name?")

    def update_option_deletenti(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                self.load_entity(self.selected)
                self.print_entity_information(update, model)
                update.message.reply_text("Type the name of entity you will delete")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            lst_enti = []
            for entity, arity, opt in self.aft_msa.entity_list:
                lst_enti.append(entity)
            if update.message.text in lst_enti:
                to_delete = []
                for entity, arity, opt in self.aft_msa.entity_list:
                    if entity == update.message.text:
                        to_delete.append(entity)
                        to_delete.append(arity)
                        to_delete.append(opt)
                        break
                print(to_delete)
                self.aft_msa.remove_entity(to_delete)
                update.message.reply_text("Did you need more entity to delete? (y/n)")
                self.operation_count += 1
            else:
                update.message.reply_text("Please type again")
        elif self.operation_count == 3:
            if self.YN_again_menu(update, 1):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                    self.load_entity(self.selected)
                    self.print_entity_information(update, model)
                    update.message.reply_text("Type name of Entity")

    def update_option_modienti_name(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                # print(model)
                self.load_entity(self.selected)
                self.print_entity_information(update, model)
                update.message.reply_text("Type the name of entity to modify")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")

        elif self.operation_count == 2:
            lst_enti = []
            for entity, arity, opt in self.aft_msa.entity_list:
                lst_enti.append(entity)
            if update.message.text in lst_enti:
                self.int_memo = lst_enti.index(update.message.text)
                self.operation_count += 1
                update.message.reply_text("Type the new name")
            else:
                update.message.reply_text("No such entity in the list. Please type again.")

        elif self.operation_count == 3:
            self.aft_msa.entity_list[self.int_memo][0] = update.message.text
            update.message.reply_text("Did you need more modify name more? (y/n)")
            self.operation_count += 1

        elif self.operation_count == 4:
            if self.YN_again_menu(update, 3):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modienti_attribute(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                # print(model)
                self.load_entity(self.selected)
                self.print_entity_information(update, model)
                update.message.reply_text("Type the name of entity to modify")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity to change attribute")

        elif self.operation_count == 2:
            lst_enti = []
            for entity, arity, opt in self.aft_msa.entity_list:
                lst_enti.append(entity)
            if update.message.text in lst_enti:
                self.int_memo = lst_enti.index(update.message.text)
                self.operation_count += 1
                update.message.reply_text("Type number of adjusted attribute")
            else:
                update.message.reply_text("No such entity in the list. Please type again.")

        elif self.operation_count == 3:
            if self.Chk_int(update, update.message.text):
                self.aft_msa.entity_list[self.int_memo][1] = update.message.text
                update.message.reply_text("Did you need more modify attribute more? (y/n)")
                self.operation_count += 1
            else:
                update.message.reply_text("Please type int")

        elif self.operation_count == 4:
            if self.YN_again_menu(update, 3):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modienti_optional(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                # print(model)
                self.load_entity(self.selected)
                self.print_entity_information(update, model)
                update.message.reply_text("Type the name of entity to modify")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity to change optional")

        elif self.operation_count == 2:
            lst_enti = []
            for entity, arity, opt in self.aft_msa.entity_list:
                lst_enti.append(entity)
            if update.message.text in lst_enti:
                self.int_memo = lst_enti.index(update.message.text)
                if self.aft_msa.entity_list[self.int_memo][2]:
                    self.aft_msa.entity_list[self.int_memo][2] = False
                else:
                    self.aft_msa.entity_list[self.int_memo][2] = True
                update.message.reply_text("Did you need more modify optional more? (y/n)")
                self.operation_count += 1
            else:
                update.message.reply_text("No such entity in the list. Please type again.")

        elif self.operation_count == 3:
            if self.YN_again_menu(update, 2):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_insert_input(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                # print(model)
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("Type the name of new input port")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            self.aft_msa.insert_input_port(update.message.text)
            update.message.reply_text("Did you need more add more? (y/n)")
            self.operation_count += 1

        elif self.operation_count == 3:
            if self.YN_again_menu(update, 2):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_insert_output(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("Type the name of new output port")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            self.aft_msa.insert_output_port(update.message.text)
            update.message.reply_text("Did you need more add more? (y/n)")
            self.operation_count += 1

        elif self.operation_count == 3:
            if self.YN_again_menu(update, 2):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_insert_exinput(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("type the name of input port that you will use for external input port")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            if update.message.text in self.aft_msa.input_ports:
                self.char_memo_1 = update.message.text
                for name, arti, opt in self.aft_msa.entity_list:
                    self.list_memo.append(name)
                update.message.reply_text(str(self.list_memo))
                update.message.reply_text("Choose entity that will be connected with input port")
                self.operation_count += 1
            else:
                update.message.reply_text("there is no such " + update.message.text + " please type again.")
        elif self.operation_count == 3:
            if update.message.text in self.list_memo:
                self.char_memo_2 = update.message.text
                update.message.reply_text(str(self.aft_msa.input_ports))
                update.message.reply_text("type the name of input port that you will use with entity")
                self.operation_count += 1
            else:
                update.message.reply_text("there is no such " + update.message.text + " please type again.")
        elif self.operation_count == 4:
            if update.message.text in self.aft_msa.input_ports:
                self.aft_msa.insert_coupling(("", self.char_memo_1), (self.char_memo_2, update.message.text))
                self.operation_count += 1
                update.message.reply_text("If you want to coupling more? (y/n)")
            else:
                update.message.reply_text("there is no such " + update.message.text + " please type again.")
        elif self.operation_count == 5:
            if self.YN_again_menu(update, 4):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_insert_exoutput(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("type the name of input port that you will use for external output port")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            if update.message.text in self.aft_msa.output_ports:
                self.char_memo_1 = update.message.text
                for name, arti, opt in self.aft_msa.entity_list:
                    self.list_memo.append(name)
                update.message.reply_text(str(self.list_memo))
                update.message.reply_text("Choose entity that will be connected with output port")
                self.operation_count += 1
            else:
                update.message.reply_text("there is no such " + update.message.text + " please type again.")
        elif self.operation_count == 3:
            if update.message.text in self.list_memo:
                self.char_memo_2 = update.message.text
                update.message.reply_text(str(self.aft_msa.output_ports))
                update.message.reply_text("type the name of output port that you will use with entity")
                self.operation_count += 1
            else:
                update.message.reply_text("there is no such " + update.message.text + " please type again.")
        elif self.operation_count == 4:
            if update.message.text in self.aft_msa.output_ports:
                self.aft_msa.insert_coupling((self.char_memo_2, update.message.text), ("", self.char_memo_1))
                self.operation_count += 1
                update.message.reply_text("If you want to coupling more? (y/n)")
            else:
                update.message.reply_text("there is no such " + update.message.text + " please type again.")
        elif self.operation_count == 5:
            if self.YN_again_menu(update, 4):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_insert_internal(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("Choose output port that you want to use to coupling")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            if update.message.text in self.aft_msa.output_ports:
                self.char_memo_1 = update.message.text
                for name, arti, opt in self.aft_msa.entity_list:
                    self.list_memo.append(name)
                update.message.reply_text(str(self.list_memo))
                update.message.reply_text("Choose entity that you will use with output port")
                self.operation_count += 1
            else:
                update.message.reply_text("there is no such " + update.message.text + " please type again.")
        elif self.operation_count == 3:
            if update.message.text in self.list_memo:
                self.char_memo_2 = update.message.text
                update.message.reply_text(str(self.aft_msa.input_ports))
                update.message.reply_text("Choose input port that you want to use to coupling")
                self.operation_count += 1
            else:
                update.message.reply_text("there is no such " + update.message.text + " please type again.")
        elif self.operation_count == 4:
            if update.message.text in self.aft_msa.input_ports:
                self.char_memo_3 = update.message.text
                update.message.reply_text(str(self.list_memo))
                update.message.reply_text("Choose entity that you will use with input port")
                self.operation_count += 1
            else:
                update.message.reply_text("there is no such " + update.message.text + " please type again.")
        elif self.operation_count == 5:
            if update.message.text in self.list_memo:
                self.aft_msa.insert_coupling((self.char_memo_2, self.char_memo_1),
                                             (update.message.text, self.char_memo_3))
                self.operation_count += 1
                update.message.reply_text("If you want to coupling more? (y/n)")
            else:
                update.message.reply_text("there is no such " + update.message.text + " please type again.")
        elif self.operation_count == 6:
            if self.YN_again_menu(update, 5):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_delete_input(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                # print(model)
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("Type port that you want to delete")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            if update.message.text in self.aft_msa.input_ports:
                self.aft_msa.input_ports.remove(update.message.text)
                if update.message.text in self.aft_msa.external_input_map.keys():
                    self.aft_msa.external_input_map.pop(update.message.text)
                pop_lst = []
                for key, values in self.aft_msa.external_input_map.items():
                    rmv_lst = []
                    i = len(values)
                    for item in values:
                        if item[1] == update.message.text:
                            if i == 1:
                                pop_lst.append(key)
                            else:
                                rmv_lst.append(item)
                                i -= 1
                    for item in rmv_lst:
                        values.remove(item)
                for key in pop_lst:
                    self.aft_msa.external_input_map.pop(key)
                pop_lst = []
                for key, values in self.aft_msa.internal_coupling_map_entity.items():
                    rmv_lst = []
                    i = len(values)
                    for item in values:
                        if item[1][1] == update.message.text:
                            if i == 1:
                                pop_lst.append(key)
                            else:
                                rmv_lst.append(item)
                                i -= 1
                    for item in rmv_lst:
                        values.remove(item)
                for key in pop_lst:
                    self.aft_msa.internal_coupling_map_entity.pop(key)
                pop_lst = []
                for key, values in self.aft_msa.internal_coupling_map_tuple.items():
                    rmv_lst = []
                    i = len(values)
                    for item in values:
                        if item[1] == update.message.text:
                            if len(values) == 1:
                                pop_lst.append(key)
                            else:
                                rmv_lst.append(item)
                                i -= 1
                    for item in rmv_lst:
                        values.remove(item)
                for key in pop_lst:
                    self.aft_msa.internal_coupling_map_tuple.pop(key)
                update.message.reply_text("Did you want delete more? (y/n)")
                self.operation_count += 1
            else:
                update.message.reply_text("Can't find that port. Please type again")

        elif self.operation_count == 3:
            if self.YN_again_menu(update, 2):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_delete_output(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                # print(model)
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("Type port that you want to delete")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            if update.message.text in self.aft_msa.output_ports:
                self.aft_msa.output_ports.remove(update.message.text)
                if update.message.text in self.aft_msa.external_output_map.keys():
                    self.aft_msa.external_output_map.pop(update.message.text)
                pop_lst = []
                for key, values in self.aft_msa.external_output_map.items():
                    rmv_lst = []
                    i = len(values)
                    for item in values:
                        if item[1] == update.message.text:
                            if i == 1:
                                pop_lst.append(key)
                            else:
                                rmv_lst.append(item)
                                i -= 1
                    for item in rmv_lst:
                        values.remove(item)
                for key in pop_lst:
                    self.aft_msa.external_output_map.pop(key)
                pop_lst = []
                for key, values in self.aft_msa.internal_coupling_map_entity.items():
                    rmv_lst = []
                    i = len(values)
                    for item in values:
                        if item[0] == update.message.text:
                            if i == 1:
                                pop_lst.append(key)
                            else:
                                rmv_lst.append(item)
                                i -= 1
                    for item in rmv_lst:
                        values.remove(item)
                for key in pop_lst:
                    self.aft_msa.internal_coupling_map_entity.pop(key)
                pop_lst = []
                for key, values in self.aft_msa.internal_coupling_map_tuple.items():
                    if key[1] == update.message.text:
                        pop_lst.append(key)
                for key in pop_lst:
                    self.aft_msa.internal_coupling_map_tuple.pop(key)
                update.message.reply_text("Did you need want delete more? (y/n)")
                self.operation_count += 1
            else:
                update.message.reply_text("Can't find that port. Please type again")
        elif self.operation_count == 3:
            if self.YN_again_menu(update, 2):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_delete_exinput(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                # print(model)
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("Type external input port that you want to delete")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            if update.message.text in self.aft_msa.external_input_map.keys():
                if len(self.aft_msa.external_input_map.get(update.message.text)) == 1:
                    self.aft_msa.remove_coupling(("", update.message.text),
                                                 (self.aft_msa.external_input_map.get(update.message.text)[0][0],
                                                  self.aft_msa.external_input_map.get(update.message.text)[0][1]))
                    update.message.reply_text("Did you need want delete more? (y/n)")
                    self.operation_count += 2
                else:
                    update.message.reply_text(self.aft_msa.external_input_map.values())
                    update.message.reply_text("Type name the name of the entity")
                    self.char_memo_1 = update.message.text
                    self.operation_count += 1
            else:
                update.message.reply_text("Cant find that port. Please type again")
        elif self.operation_count == 3:
            if update.message.text in self.aft_msa.entity_list:
                i = 0
                T = True
                while T:
                    _compared = self.aft_msa.external_input_map.get(self.char_memo_1)[i][0]
                    if _compared == update.message.text:
                        T = False
                    else:
                        i += 1
                self.aft_msa.remove_coupling(("", self.char_memo_1),
                                             (self.aft_msa.external_input_map.get(self.char_memo_1)[i][0],
                                              self.aft_msa.external_input_map.get(self.char_memo_1)[i][1]))
                update.message.reply_text("Did you need want delete more? (y/n)")
                self.operation_count += 1
            else:
                update.message.reply_text("Please type again")
        elif self.operation_count == 4:
            if self.YN_again_menu(update, 3):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_delete_exoutput(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                # print(model)
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("Type external output port that you want to delete")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            if update.message.text in self.aft_msa.external_output_map.keys():
                if len(self.aft_msa.external_output_map.get(update.message.text)) == 1:
                    self.aft_msa.remove_coupling((self.aft_msa.external_output_map.get(update.message.text)[0][0],
                                             self.aft_msa.external_output_map.get(update.message.text)[0][1]), ("", update.message.text))
                    update.message.reply_text("Did you need want delete more? (y/n)")
                    self.operation_count += 2
                else:
                    update.message.reply_text(self.aft_msa.external_output_map.values())
                    update.message.reply_text("Type name the name of the entity")
                    self.char_memo_1 = update.message.text
                    self.operation_count += 1
            else:
                update.message.reply_text("Cant find that port. Please type again")
        elif self.operation_count == 3:
            if update.message.text in self.aft_msa.entity_list:
                i = 0
                T = True
                while T:
                    _compared = self.aft_msa.external_output_map.get(self.char_memo_1)[i][0]
                    if _compared == update.message.text:
                        T = False
                    else:
                        i += 1
                self.aft_msa.remove_coupling(("", self.char_memo_1),
                                             (self.aft_msa.external_output_map.get(self.char_memo_1)[i][0],
                                              self.aft_msa.external_output_map.get(self.char_memo_1)[i][1]))
                update.message.reply_text("Did you need want delete more? (y/n)")
                self.operation_count += 1
            else:
                update.message.reply_text("Please type again")
        elif self.operation_count == 4:
            if self.YN_again_menu(update, 3):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_delete_internal(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                # print(model)
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("Type entity with output port "
                                          "that included in internal port you want to delete")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            if update.message.text in self.aft_msa.internal_coupling_map_entity.keys():
                self.char_memo_1 = update.message.text
                update.message.reply_text("Type output port "
                                          "that included in internal port you want to delete")
                self.operation_count += 1
            else:
                update.message.reply_text("Can't find that entity in the internal coupling")
                update.message.reply_text("Type entity with output port "
                                          "that included in internal port you want to delete")
        elif self.operation_count == 3:
            self.list_memo = []
            for enti, inport in self.aft_msa.internal_coupling_map_entity[self.char_memo_1]:
                self.list_memo.append(enti)
            if update.message.text in self.list_memo:
                self.char_memo_2 = update.message.text
                if self.list_memo.count(update.message.text) == 1:
                    self.char_memo_4 = str(self.list_memo.index(update.message.text))
                else:
                    for i in range(len(self.list_memo)):
                        if self.list_memo[i] == update.message.text:
                            self.char_memo_4 += str(i)
                    print(self.char_memo_4)
                update.message.reply_text("Type entity with input port "
                                          "that included in internal port you want to delete")
                self.operation_count += 1
            else:
                update.message.reply_text("Can't find that port. Please type again")

        elif self.operation_count == 4:
            self.list_memo = []
            for i in range(len(self.char_memo_4)):
                self.list_memo.append(
                    self.aft_msa.internal_coupling_map_entity[self.char_memo_1][int(self.char_memo_4[i])][1][0])
            print(self.list_memo)
            if update.message.text in self.list_memo:
                self.char_memo_3 = update.message.text
                for i in range(len(self.list_memo)):
                    if self.list_memo[i] == update.message.text:
                        self.char_memo_5 += self.char_memo_4[i]
                print(self.char_memo_5)
                update.message.reply_text("Type input port "
                                          "that included in internal port you want to delete")
                self.operation_count += 1
            else:
                update.message.reply_text("Can't find that entity. Please type again")
        elif self.operation_count == 5:
            self.list_memo = []
            for i in range(len(self.char_memo_5)):
                self.list_memo.append(
                    self.aft_msa.internal_coupling_map_entity[self.char_memo_1][int(self.char_memo_5[i])][1][1])
            print(self.list_memo)
            if update.message.text in self.list_memo:
                self.aft_msa.remove_coupling((self.char_memo_1, self.char_memo_2),
                                             (self.char_memo_3, update.message.text))
                update.message.reply_text("Did you need want delete more? (y/n)")
                self.operation_count += 1
            else:
                update.message.reply_text("Can't find that port. Please type again")

        elif self.operation_count == 6:
            if self.YN_again_menu(update, 5):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_change_input(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("Type port that you want to change")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            if update.message.text in self.aft_msa.input_ports:
                self.char_memo_1 = update.message.text
                update.message.reply_text("Type the new name of the port")
                self.operation_count += 1
            else:
                update.message.reply_text("Can't find that port. Please type again.")
        elif self.operation_count == 3:
            self.aft_msa.input_ports[self.aft_msa.input_ports.index(self.char_memo_1)] = update.message.text
            if self.char_memo_1 in self.aft_msa.external_input_map.keys():
                self.aft_msa.external_input_map[update.message.text] = self.aft_msa.external_input_map.pop(self.char_memo_1)
            for item in self.aft_msa.external_input_map.values():
                for i in range(len(item)):
                    if item[i][1] == self.char_memo_1:
                        item[i][1] = update.message.text
            for item in self.aft_msa.internal_coupling_map_entity.values():
                for i in range(len(item)):
                    if item[i][1][1] == self.char_memo_1:
                        item[i][1][1] = update.message.text
            for item in self.aft_msa.internal_coupling_map_tuple.values():
                for i in range(len(item)):
                    if self.char_memo_1 == item[i][1]:
                        e = item[i][0]
                        item[i] = (e, update.message.text)
            update.message.reply_text("Did you need want change more? (y/n)")
            self.operation_count += 1
        elif self.operation_count == 4:
            if self.YN_again_menu(update, 3):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def update_option_modiport_change_output(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                model = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                self.load_entity(self.selected)
                self.print_port_information(update, model)
                update.message.reply_text("Type port that you want to change")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            if update.message.text in self.aft_msa.output_ports:
                self.char_memo_1 = update.message.text
                update.message.reply_text("Type the new name of the port")
                self.operation_count += 1
            else:
                update.message.reply_text("Can't find that port. Please type again.")
        elif self.operation_count == 3:
            self.aft_msa.output_ports[self.aft_msa.output_ports.index(self.char_memo_1)] = update.message.text
            if self.char_memo_1 in self.aft_msa.external_output_map.keys():
                self.aft_msa.external_output_map[update.message.text] = self.aft_msa.external_output_map.pop(self.char_memo_1)
            for item in self.aft_msa.external_output_map.values():
                for i in range(len(item)):
                    if item[i][1] == self.char_memo_1:
                        item[i][1] = update.message.text
            for item in self.aft_msa.internal_coupling_map_entity.values():
                for i in range(len(item)):
                    if item[i][0] == self.char_memo_1:
                        item[i][0] = update.message.text
            for item in self.aft_msa.internal_coupling_map_tuple.keys():
                for i in range(int(len(item) / 2)):
                    if self.char_memo_1 == item[i * 2 + 1]:
                        self.aft_msa.internal_coupling_map_tuple[
                            item[i], update.message.text] = self.aft_msa.internal_coupling_map_tuple.pop(item)
            update.message.reply_text("Did you need want change more? (y/n)")
            self.operation_count += 1
        elif self.operation_count == 4:
            if self.YN_again_menu(update, 3):
                self.save_entity()
                self.clear_system()
            else:
                if update.message.text == "y":
                    self.save_entity()
                    self.clear_memo()
                    self.print_entity_db(update)
                    update.message.reply_text("Type name of Entity")

    def interactive_pruning(self, update):
        if self.operation_count == 0:
            self.print_entity_db(update)
            update.message.reply_text("Type name of Entity")
            self.operation_count += 1
        elif self.operation_count == 1:
            if update.message.text in self.model_db.keys():
                self.selected = update.message.text
                self.load_entity(self.selected)
                root_entity = self.sm.esm.import_system_entity_structure(self.model_db[self.selected])
                self.pes = root_entity.clone()
                self.pes.set_name("pruned_" + self.pes.get_name())
                self.pes.entity_list = self.pes.check_validity()
                update.message.reply_text("Type anything to process")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found")
                update.message.reply_text("Type name of Entity")
        elif self.operation_count == 2:
            fmt = "{name: <10}\t{arity: <5}\t{opt: <5}"
            update.message.reply_text("List of entities to pruning")
            _str = ""
            for entity in self.pes.entity_list:
                _str += fmt.format(name=entity[0], arity=entity[1], opt=entity[2]) + "\n"
            update.message.reply_text(_str)
            update.message.reply_text("Select entity to prune")
            self.operation_count += 1

        elif self.operation_count == 3:
            if True in list(map(lambda x: x[0] == update.message.text, self.pes.entity_list)):
                self.char_memo_1 = update.message.text
                update.message.reply_text("Type anything to process")
                self.operation_count += 1
            else:
                update.message.reply_text("[ERR] Entity Not Found. Please type again")

        elif self.operation_count == 4:
            for entity in self.pes.entity_list:
                if entity[0] == self.char_memo_1:
                    if entity[2]:
                        update.message.reply_text("> The sub-entity {0} is optional".format(entity[0]))
                        update.message.reply_text("> Select(s), Remove(n)")
                        self.operation_count += 1
                    else:
                        for entity in self.pes.entity_list:
                            if entity[0] == self.char_memo_1:
                                if type(entity[1]) is str:
                                    update.message.reply_text("> The arity of {0} is {1}".format(entity[0], entity[1]))
                                    update.message.reply_text("> Enter arity:")
                        self.operation_count += 2

        elif self.operation_count == 5:
            for entity in self.pes.entity_list:
                if entity[0] == self.char_memo_1:
                    if update.message.text == 's':
                        entity[2] = False
                        if type(entity[1]) is str:
                            update.message.reply_text("> The arity of {0} is {1}".format(entity[0], entity[1]))
                            update.message.reply_text("> Enter arity:")
                        self.operation_count += 1
                    elif update.message.text == 'n':
                        self.list_memo = entity
                        update.message.reply_text("Enter anything to continue")
                        self.operation_count += 2
                    else:
                        update.message.reply_text("Please type only s or n")
                        update.message.reply_text("> Select(s), Remove(n)")

        elif self.operation_count == 6:
            for entity in self.pes.entity_list:
                if entity[0] == self.char_memo_1:
                    entity[1] = update.message.text
                    update.message.reply_text("Enter anything to continue")
                    self.operation_count += 1

        elif self.operation_count == 7:
            if len(self.list_memo) > 0:
                self.pes.remove_entity(self.list_memo)
            self.pes.entity_list = self.pes.check_validity()
            if not len(self.pes.entity_list) == 0:
                fmt = "{name: <10}\t{arity: <5}\t{opt: <5}"
                update.message.reply_text("List of entities to pruning")
                _str = ""
                for entity in self.pes.entity_list:
                    _str += fmt.format(name=entity[0], arity=entity[1], opt=entity[2]) + "\n"
                update.message.reply_text(_str)
                update.message.reply_text("Select entity to prune")
                self.operation_count -= 4
            else:
                update.message.reply_text("Do you want to synthesize executable? (y/n)")
                self.operation_count += 1

        elif self.operation_count == 8:
            if self.YN_nextstep_menu(update, 6):
                self.ra = RuntimeAttribute()
                self.list_memo = self.pes.get_core_attribute().retrieve_entities()
                self.int_memo = len(self.list_memo)
            update.message.reply_text("Press enter anything to continue.")

        elif self.operation_count == 9:
            if not self.int_memo == 0:
                update.message.reply_text("Do you want to add model instance? (y/n)")
                self.operation_count += 1
            else:
                self.operation_count += 5
                update.message.reply_text("Press enter anything to continue.")

        elif self.operation_count == 10:
            if self.YN_nextstep_menu(update, 4):
                self.ra.insert_entity(self.list_memo[len(self.list_memo)-self.int_memo][0])
                update.message.reply_text(">>> Enter path of {}'s"
                              " model instance: ".format(self.list_memo[len(self.list_memo)-self.int_memo][0]))

        elif self.operation_count == 11:
            self.ra.insert_model_path(self.list_memo[len(self.list_memo)-self.int_memo][0], update.message.text)
            update.message.reply_text(">>> Do you want to add domain instance? (y/n)")
            self.operation_count += 1

        elif self.operation_count == 12:
            if self.YN_nextstep_menu(update, 2):
                update.message.reply_text(">>> Enter path of {}'s domain instance"
                                          ": ".format(self.list_memo[len(self.list_memo)-self.int_memo][0]))

        elif self.operation_count == 13:
            self.ra.insert_domain_path((self.list_memo[len(self.list_memo)-self.int_memo][0], update.message.text))
            self.int_memo -= 1
            if not self.int_memo == 0:
                update.message.reply_text("Press enter anything to continue.")
                self.operation_count -= 4
            else:
                update.message.reply_text("Press enter anything to continue.")
                self.operation_count += 1

        elif self.operation_count == 14:
            if not self.ra is None:
                self.pes.insert_attribute(self.ra)
            update.message.reply_text(">>> Pruned Entity Structure <<< ")

            fmt = "{0: <10}{name: <15}\t{arity: <5}\t{opt: <5}"
            _str = ""
            _str += "Name: " + self.pes.entity_name + "\n"
            _str += fmt.format("Entities: ", name="Name", arity="Arity", opt="Optional") + "\n"
            entities = self.pes.core_attribute.retrieve_entities()
            for idx, entity in enumerate(entities):
                _str += "\t" + fmt.format(idx + 1, name=entity[0], arity=entity[1], opt=entity[2]) + "\n"

            update.message.reply_text(_str)
            update.message.reply_text("Stored in pes_db")
            pes_path = os.path.join(os.path.dirname(self.entity_path), "pes_db")

            esm = EntityManager()
            entity = esm.create_entity_structure()
            entity.set_core_attribute(self.aft_msa)
            esm.create_system(entity)
            self.pes.export_system_entity_structure(self.pes, pes_path, self.pes.get_name() + ".json")
            self.clear_system()
