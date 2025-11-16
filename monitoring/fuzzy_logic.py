from simpful import *

class FuzzyRiskModel:
    def __init__(self):

        self.FS = FuzzySystem()

        # === Вихідна змінна Risk 0-100 ===
        S = LinguisticVariable([
            TrapezoidFuzzySet(0, 0, 20, 40, term="Low"),
            TrapezoidFuzzySet(30, 50, 60, 80, term="Medium"),
            TrapezoidFuzzySet(70, 85, 100, 100, term="High"),
        ], universe_of_discourse=[0,100])

        self.FS.add_linguistic_variable("Risk", S)

        # === Універсальні вхідні параметри (поки що 0–100) ===
        params = ["A", "B", "C", "D"]

        for p in params:
            LV = LinguisticVariable([
                TrapezoidFuzzySet(0, 0, 20, 40, term="Low"),
                TrapezoidFuzzySet(30, 50, 60, 80, term="Medium"),
                TrapezoidFuzzySet(70, 85, 100, 100, term="High"),
            ], universe_of_discourse=[0,100])
            self.FS.add_linguistic_variable(p, LV)

        # === Універсальні правила ===
        RULES = [
            # HIGH risk
            "IF A IS High OR B IS High OR C IS High OR D IS High THEN Risk IS High",

            # Medium risk
            "IF A IS Medium AND B IS Medium THEN Risk IS Medium",

            # Low risk
            "IF A IS Low AND B IS Low AND C IS Low AND D IS Low THEN Risk IS Low",
        ]

        self.FS.add_rules(RULES)

    def evaluate(self, values):
        """
        values = [A, B, C, D] normalized to 0-100
        """

        A, B, C, D = values

        self.FS.set_variable("A", A)
        self.FS.set_variable("B", B)
        self.FS.set_variable("C", C)
        self.FS.set_variable("D", D)

        result = self.FS.Mamdani_inference()
        return result["Risk"]
