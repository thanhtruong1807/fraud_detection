from pydantic import BaseModel, Field

class Txn(BaseModel):
    type: str = Field(..., description="Transaction type, e.g. CASH_OUT/TRANSFER/...")
    amount: float = Field(..., ge=0)
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float