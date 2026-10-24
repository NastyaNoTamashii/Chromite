import Chromite
from Chromite import Color

Chromite.clear()

Chromite.Write("$red$Welcome! :tada:$reset$", pos=(24, 1)).display()
print('\n\n')

mytree = {
    "MyProject/": {
        "config/": [
            "db.config.js",
            "env.config.js"
        ],
        "services/": [
            "email.service.js",
            "payment.service.js"
        ],
        "utils/": [
            "email.utils.js",
            "payment.utils.js",
            "logger.js"
        ]
    }
}

Chromite.Tree(
    mytree,
    compose=Color.Gold,
    branch_compose=Color.Red,
    style=Chromite.TreeStyle.Rounded
).display()