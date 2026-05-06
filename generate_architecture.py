from graphviz import Digraph

dot = Digraph("CreditAppArchitecture", format="png")

# ======================
# Nodes
# ======================

dot.node("UI", "User / Frontend UI")

dot.node("MAIN", "Main App (Flask)\nPort 5005")

dot.node("SIGNIN", "Sign-In Service\nPort 5001")
dot.node("CUST", "Customer Info Service\nPort 5002")
dot.node("CREDIT", "CreditScan Service\nPort 5003")
dot.node("FRAUD", "FraudRisk Service\nPort 5004")
dot.node("APPID", "AppID Service\nPort 5009")

dot.node("DB", "JSON Database\ncredit_applications_db.json")

dot.node("AUTH", "API Key Security Layer\n(auth.py / X-API-Key)")
dot.node("TLS", "Optional HTTPS/TLS Layer")

# ======================
# Edges (Flow)
# ======================

dot.edge("UI", "MAIN")

dot.edge("MAIN", "SIGNIN")
dot.edge("MAIN", "CUST")
dot.edge("MAIN", "CREDIT")
dot.edge("MAIN", "FRAUD")

dot.edge("CREDIT", "APPID")

dot.edge("MAIN", "DB")

# ======================
# Security Layer (annotation style)
# ======================

dot.edge("AUTH", "SIGNIN", style="dashed")
dot.edge("AUTH", "CUST", style="dashed")
dot.edge("AUTH", "CREDIT", style="dashed")
dot.edge("AUTH", "FRAUD", style="dashed")
dot.edge("AUTH", "APPID", style="dashed")

dot.edge("TLS", "MAIN", style="dotted")
dot.edge("TLS", "SIGNIN", style="dotted")
dot.edge("TLS", "CUST", style="dotted")
dot.edge("TLS", "CREDIT", style="dotted")
dot.edge("TLS", "FRAUD", style="dotted")
dot.edge("TLS", "APPID", style="dotted")

# ======================
# Render PNG
# ======================

output_path = dot.render("credit_app_architecture", view=True)

print("PNG generated at:", output_path)