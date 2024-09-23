from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import httpx
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Configuration
UNITY_ENDPOINT = os.getenv("UNITY_ENDPOINT", "http://localhost:5000/receive-code")

# Predefined C# code
PREDEFINED_CSHARP_CODE = '''
using UnityEngine;
using System.Collections.Generic;
public class VRBarChart : MonoBehaviour
{
    [System.Serializable]
    public class BarData
    {
        public string clusterName;
        public float avgGrowthQTD;
    }
    public List<BarData> data = new List<BarData>();
    public float barWidth = 0.5f;
    public float barSpacing = 0.2f;
    public float scaleFactor = 1f / 1000000f; // Scale down the values for better visualization
    public Color barColor = Color.blue;
    void Start()
    {
        LoadData();
        CreateBarChart();
    }
    void LoadData()
    {
        // Hardcoded data from the JSON
        string[] clusterNames = {
            "ANDHRA PRADESH AND TELANGANA", "DELHI AND HARYANA", "ENTERPRISE CLUSTER 1",
            "ENTERPRISE CLUSTER 2", "GUJARAT", "KARNATAKA", "KERALA", "MAHARASHTRA",
            "OTHERS", "PUNJAB AND CHANDIGARH", "TAMIL NADU", "UTTAR PRADESH", "WEST BENGAL"
        };
        float[] avgGrowthQTD = {
            6026898.43f, 16943708.9f, 3613331.62f, 2707869.34f, 5402325.55f,
            6211860.81f, 7163991.95f, 15753334.37f, 0f, 5629525.28f,
            3345712.21f, 2236505.86f, 3592192.02f
        };
        for (int i = 0; i < clusterNames.Length; i++)
        {
            data.Add(new BarData { clusterName = clusterNames[i], avgGrowthQTD = avgGrowthQTD[i] });
        }
    }
    void CreateBarChart()
    {
        for (int i = 0; i < data.Count; i++)
        {
            CreateBar(i, data[i]);
        }
    }
    void CreateBar(int index, BarData barData)
    {
        float xPosition = index * (barWidth + barSpacing);
        float barHeight = barData.avgGrowthQTD * scaleFactor;
        // Create bar
        GameObject bar = GameObject.CreatePrimitive(PrimitiveType.Cube);
        bar.transform.SetParent(transform);
        bar.transform.localPosition = new Vector3(xPosition, barHeight / 2, 0);
        bar.transform.localScale = new Vector3(barWidth, barHeight, barWidth);
        bar.GetComponent<Renderer>().material.color = barColor;
        // Create label for cluster name
        CreateTextMesh(barData.clusterName, new Vector3(xPosition, -0.5f, 0), 90);
        // Create label for value
        CreateTextMesh(barData.avgGrowthQTD.ToString("N0"), new Vector3(xPosition, barHeight + 0.5f, 0), 0);
    }
    void CreateTextMesh(string text, Vector3 position, float xRotation)
    {
        GameObject textObj = new GameObject("Label");
        textObj.transform.SetParent(transform);
        textObj.transform.localPosition = position;
        textObj.transform.localRotation = Quaternion.Euler(xRotation, 0, 0);
        TextMesh textMesh = textObj.AddComponent<TextMesh>();
        textMesh.text = text;
        textMesh.fontSize = 14;
        textMesh.alignment = TextAlignment.Center;
        textMesh.anchor = TextAnchor.MiddleCenter;
    }
}
'''

@app.post("/send-predefined-csharp-code/")
async def send_predefined_csharp_code():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(UNITY_ENDPOINT, json={"code": PREDEFINED_CSHARP_CODE}, timeout=30.0)
            response.raise_for_status()
            return {"message": "Predefined C# code sent to Unity successfully", "unity_response": response.json()}
    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending code to Unity: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# To run this FastAPI app:
# uvicorn main:app --reload
# Or if this script is named main.py:
# python main.py