import axios from "axios";

/**
 * Represents Responsible AI (RAI) metrics, including an overall score and sub-metrics.
 */
export interface RaiMetrics {
  /**
   * The overall RAI score.
   */
  raiScore: number;
  /**
   * The biasness metric.
   */
  biasness: number;
  /**
   * The truthfulness metric.
   */
  truthfulness: number;
  /**
   * The fairness metric.
   */
  fairness: number;
  /**
   * The groundedness metric.
   */
  groundedness: number;
}

/**
 * Defines the possible input types for RAI metric calculation.
 */
export type RaiInput =
  | { type: "text"; value: string }
  | { type: "image"; value: string } // URL for image
  | { type: "audio"; value: string } // URL for audio
  | { type: "video"; value: string }; // URL for video

/**
 * Asynchronously retrieves RAI metrics for a given AI response, which can be text or media.
 *
 * @param input An object containing the type and value (text or media URL) of the AI response to be evaluated.
 * @returns A promise that resolves to a RaiMetrics object containing the RAI score and sub-metrics.
 */

export async function getRaiMetrics(input: RaiInput): Promise<RaiMetrics> {
  try {
    // Make a POST request to the backend API
    const response = await axios.post(
      "http://127.0.0.1:8000/api/v1/agents/get-rai-metrics",
      {
        type: input.type,
        value: input.value,
      }
    );

    // Extract the first item from the response data
    const data = response.data[0];

    // Map the response to the RaiMetrics interface
    const metrics: RaiMetrics = {
      raiScore: data.raiScore,
      biasness: data.biasness,
      truthfulness: data.truthfulness ?? 0, // Default to 0 if not provided
      fairness: data.fairness,
      groundedness: data.groundedness ?? 0, // Default to 0 if not provided
    };

    return metrics;
  } catch (error) {
    console.error("Error fetching RAI metrics:", error);
    throw new Error("Failed to fetch RAI metrics from the backend.");
  }
}
