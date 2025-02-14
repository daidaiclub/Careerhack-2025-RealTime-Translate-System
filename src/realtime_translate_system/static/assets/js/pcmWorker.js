class PCMWorkletProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.quantaPerFrame = 12; // 每個 frame 包含 12 個 128-sample 片段
    this.quantaCount = 0;
    this.frame = new Int16Array(128 * this.quantaPerFrame);
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || input.length === 0) {
      return true;
    }

    const channelData = input[0];
    const offset = 128 * this.quantaCount;

    // 轉換 Float32 到 Int16
    for (let i = 0; i < channelData.length; i++) {
      const s = Math.max(-1, Math.min(1, channelData[i]));
      this.frame[offset + i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }

    this.quantaCount++;
    if (this.quantaCount === this.quantaPerFrame) {
      this.port.postMessage(this.frame);
      this.quantaCount = 0;
    }

    return true;
  }
}

registerProcessor("pcm-worker", PCMWorkletProcessor);
