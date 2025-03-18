import base64

from django.conf import settings
from openai import OpenAI


class PlantDiseaseChecker:
    def __init__(self):
        self.openai = OpenAI(
            api_key=settings.OPENAI_PLANT_DISEASE_API_KEY,
        )

    def analyze_by_url(self, image_url):
        """
        Analyze plant image and identify potential diseases.

        Args:
            image_url: URL to the image to be analyzed

        Returns:
            dict: Analysis results from the OpenAI API
        """
        response = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this plant image and identify any diseases or issues. Describe the symptoms visible, the potential disease name, severity level, and recommended treatments.",  # noqa: E501
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                    ],
                },
            ],
        )

        return {
            "analysis": response.choices[0].message.content,
            "raw_response": response,
        }

    def analyze_base64(self, image_base64):
        """
        Analyze plant image from base64 string and identify potential diseases.

        Args:
            image_base64: Base64 encoded image string

        Returns:
            dict: Analysis results from the OpenAI API
        """
        response = self.openai.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Analyze this plant image and identify any diseases or issues. Describe the symptoms visible, the potential disease name, severity level, and recommended treatments. Response in Bahasa Indonesia",  # noqa: E501
                        },
                        {
                            "type": "input_image",
                            # "image": {"url": f"data:image/jpeg;base64,{image_base64}"},  # noqa: E501, ERA001
                            "image_url": "https://asset-2.tstatic.net/bangka/foto/bank/images/biduri_20171021_081119.jpg",
                        },
                    ],
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "plant_disease_analysis",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "disease_name": {"type": "string"},
                            "confidence": {"type": "number"},
                            "symptoms": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                            },
                            "treatment_recommendations": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "preventive_measures": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "mini_article": {
                                "type": "string",
                                "description": "A concise, informative article about the disease",  # noqa: E501
                            },
                        },
                        "required": [
                            "disease_name",
                            "confidence",
                            "symptoms",
                            "severity",
                            "treatment_recommendations",
                            "preventive_measures",
                            "mini_article",
                        ],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            },
        )

        # print(response.output_text)  # noqa: ERA001
        # print(json.dumps(json.loads(response.output_text), indent=4))  # noqa: ERA001
        return response  # noqa: RET504

    def analyze_by_image_field(self, image_field):
        """
        Analyze plant disease from a Django ImageField.

        Args:
            image_field: Django ImageField instance

        Returns:
            dict: Analysis results from the OpenAI API
        """
        # Make sure the file is open
        image_field.open()

        # Read the file content
        image_content = image_field.read()

        # Close the file
        image_field.close()

        # Convert to base64
        image_base64 = base64.b64encode(image_content).decode("utf-8")

        # Use the base64 analyze method
        return self.analyze_base64(image_base64)
