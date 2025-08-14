from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Dict, Any

class Token(BaseModel):
    iat: datetime = Field(..., description="Issued at time")
    exp: datetime = Field(..., description="Expiration time")
    
    @classmethod
    def from_timestamps(cls, iat_timestamp: float, exp_timestamp: float) -> "Token":
        """
        Create a Token instance from Unix timestamps
        
        Args:
            iat_timestamp: Issued at time as Unix timestamp
            exp_timestamp: Expiration time as Unix timestamp
            
        Returns:
            Token: A new Token instance
        """
        return cls(
            iat=datetime.fromtimestamp(iat_timestamp),
            exp=datetime.fromtimestamp(exp_timestamp)
        )
    
    @model_validator(mode='before')
    @classmethod
    def validate_timestamps(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validator that allows creation of a Token from a dict with timestamp values
        
        This enables automatic conversion when data comes from JWT payload
        """
        if isinstance(data, dict):
            # If we have numeric timestamps in the dict, convert them to datetime objects
            if 'iat' in data and isinstance(data['iat'], (int, float)):
                data['iat'] = datetime.fromtimestamp(data['iat'])
            
            if 'exp' in data and isinstance(data['exp'], (int, float)):
                data['exp'] = datetime.fromtimestamp(data['exp'])
                
        return data
    
    def to_timestamps(self) -> Dict[str, float]:
        """
        Convert the Token's datetime fields to Unix timestamps
        
        Returns:
            Dict[str, float]: A dictionary with 'iat' and 'exp' as Unix timestamps
        """
        return {
            "iat": self.iat.timestamp(),
            "exp": self.exp.timestamp()
        }
