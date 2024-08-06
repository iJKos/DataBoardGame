from DataBoardGame.card import CardDeck, EmloyeeCard, employee_card_list, EmployeeRoles
from DataBoardGame import globalvars as glb
from DataBoardGame.resources import Resources, ResourceType, money_gain_per_insight, ResourceConvertion


def resource_type_to_role_mapping(resource_type: ResourceType):
    if resource_type == ResourceType.dashboard:
        return EmployeeRoles.BI
    if resource_type == ResourceType.rawdata:
        return EmployeeRoles.DE
    if resource_type == ResourceType.datamart:
        return EmployeeRoles.SA
    if resource_type == ResourceType.insight:
        return EmployeeRoles.BA
    if resource_type == ResourceType.money:
        return EmployeeRoles.PM


class GameBoard:
    employee_deck: CardDeck
    # project_deck: CardDeck
    # specials_deck: CardDeck

    def __str__(self) -> str:
        return f'employee_deck:{self.employee_deck}'

    def __init__(self) -> None:
        self.employee_deck = CardDeck(glb.MAX_EMPLOYEE_OPEN_CARDS, employee_card_list)

    def __hash__(self) -> int:
        return hash(self.employee_deck)

    def __eq__(self, other):
        if not isinstance(other, GameBoard):
            return NotImplemented
        return self.employee_deck == other.employee_deck

    def pre_game_init(self) -> None:
        self.employee_deck.pre_game_init()

    def to_dict(self):
        res = {}
        res.update(self.employee_deck.to_dict())
        # res.update(self.project_deck.to_dict())
        # res.update(self.specials_deck.to_dict())
        return res


class PlayerBoard:
    resources: Resources
    last_generated_resource: ResourceType

    money_gain = money_gain_per_insight(glb.MONEY_PER_INSIGHT)

    convertion_rules = {
        ResourceType.rawdata: ResourceConvertion(Resources(), Resources(raw_data=1)),
        ResourceType.datamart: ResourceConvertion(Resources(raw_data=2), Resources(marts=1)),
        ResourceType.dashboard: ResourceConvertion(Resources(marts=2), Resources(dashboards=1)),
        ResourceType.insight: ResourceConvertion(Resources(dashboards=2), Resources(insights=1)),
    }

    employees = {EmployeeRoles.BA: [], EmployeeRoles.DE: [], EmployeeRoles.BI: [], EmployeeRoles.SA: []}

    employees_limits = {EmployeeRoles.BA: 2, EmployeeRoles.DE: 2, EmployeeRoles.BI: 2, EmployeeRoles.SA: 2}

    def __hash__(self) -> int:
        return hash(
            (
                self.resources,
                self.last_generated_resource,
                self.money_gain,
                frozenset(sorted(self.convertion_rules.items())),  # Convert to frozenset for hashing
                frozenset(sorted((role, tuple(sorted(employees))) for role, employees in self.employees.items())),
                frozenset(sorted(self.employees_limits.items())),
            )
        )

    def __eq__(self, other):
        if not isinstance(other, PlayerBoard):
            return NotImplemented
        return (
            self.resources == other.resources
            and self.last_generated_resource == other.last_generated_resource
            and self.money_gain == other.money_gain
            and self.convertion_rules == other.convertion_rules
            and self.employees == other.employees
            and self.employees_limits == other.employees_limits
        )

    def employees_count(self):
        res = 0
        for key, value in self.employees.items():
            res += len(value)
        return res

    def to_dict(self):
        res_dict = {}

        res_dict['resources'] = self.resources.to_dict()
        res_dict['money_gain'] = self.money_gain.to_dict()

        res_dict['convertion_rules'] = {str(key): value.to_dict() for key, value in self.convertion_rules.items()}

        res_dict['employees'] = {}
        for role, cards in self.employees.items():
            for card in cards:
                res_dict['employees'][str(hash(card)) + '_' + str(role.value)] = True

        res_dict['employees_limits'] = {str(key.value): value for key, value in self.employees_limits.items()}

        return res_dict

    def __str__(self):
        """
        Return a string representation of the PlayerBoard object.
        """
        return f'\t resources={self.resources} \n\t salary={self.calc_salary().resource_to_give} \n\t empl={self.employed_count()})'

    def __init__(self) -> None:
        self.resources = Resources(5, 0, 0, 5, 10)
        self.last_generated_resource = None

    def employed_count(self):
        return [(role, len(employee_list)) for role, employee_list in self.employees.items()]

    def calc_salary(self):
        salary = ResourceConvertion(Resources(), Resources())
        for role, employee_list in self.employees.items():
            for employee in employee_list:
                salary += employee.salary

        return salary

    def check_is_salary_available(self):
        return self.resources.check_pay_aval(self.calc_salary())

    def pay_salary(self):
        return self.resources.apply_resource_conversion(self.calc_salary())

    def get_employee_limits(self):
        return self.employees_limits

    def get_employee_list(self):
        result = []
        for role, employee_list in self.employees.items():
            for employee in employee_list:
                result.append((employee, role))
        return result

    def get_available_roles(self):
        limits = self.get_employee_limits()
        result = []
        for role, employee_list in self.employees.items():
            if len(employee_list) < limits[role]:
                result.append(role)
        return result

    def hire_employee(self, employee: EmloyeeCard, role: EmployeeRoles):
        self.employees[role].append(employee)

    def fire_employee(self, employee: EmloyeeCard):
        for role, employee_list in self.employees.items():
            if employee in employee_list:
                employee_list.remove(employee)
                return

    def generate_money(self):
        self.resources.apply_resource_scale(self.money_gain)

    def check_pay_resource_to_player(self, resource_type):
        resource_gain = ResourceConvertion(Resources(), Resources())
        resource_gain += self.convertion_rules[resource_type]
        for empl in self.employees[resource_type_to_role_mapping(resource_type)]:
            resource_gain += empl.basic_resource_conversion[resource_type_to_role_mapping(resource_type)]
        return self.resources.check_pay_aval(resource_gain)

    def action_pay_resource_to_player(self, resource_type):
        resource_gain = ResourceConvertion(Resources(), Resources())
        resource_gain += self.convertion_rules[resource_type]
        for empl in self.employees[resource_type_to_role_mapping(resource_type)]:
            if empl.role == resource_type_to_role_mapping(resource_type):
                resource_gain += empl.motivated_resource_conversion[resource_type_to_role_mapping(resource_type)]
            else:
                resource_gain += empl.basic_resource_conversion[resource_type_to_role_mapping(resource_type)]

        self.resources.apply_resource_conversion(resource_gain)
        self.last_generated_resource = resource_type


class PlayerDeck:
    q = 0

    def to_dict(self):
        return {}

    def __hash__(self) -> int:
        return hash(self.q)

    def __eq__(self, value: object) -> bool:
        return True
