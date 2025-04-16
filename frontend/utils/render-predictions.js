// This function will be used to draw the bounding boxes on the canvas
export const renderPrediction = (predictions, context, imageElement, saveDetection) => {
  predictions.forEach((prediction) => {
    // Draw the bounding box
    context.beginPath();
    context.rect(
      prediction.bbox[0],  // x position
      prediction.bbox[1],  // y position
      prediction.bbox[2],  // width
      prediction.bbox[3]   // height
    );
    context.lineWidth = 2;
    context.strokeStyle = "red";
    context.fillStyle = "red";
    context.stroke();
    context.fillText(
      `${prediction.class} (${Math.round(prediction.score * 100)}%)`,
      prediction.bbox[0],
      prediction.bbox[1] > 10 ? prediction.bbox[1] - 5 : 10
    );

    // Save cropped detection if needed
    const croppedImage = imageElement
      .getContext("2d")
      .getImageData(
        prediction.bbox[0],
        prediction.bbox[1],
        prediction.bbox[2],
        prediction.bbox[3]
      );
    saveDetection({
      label: prediction.class,
      timestamp: new Date().toLocaleTimeString(),
      image: croppedImage,
    });
  });
};
