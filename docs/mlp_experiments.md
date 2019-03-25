## Experiment day 1 (Monday 24th)

### Approach 1:
- Complex NN architecture, lots of layers lots of units, on datasets of size 1000 - 10000. Model overfit data severely see 1-4 in smpl:thousand & smpl:tenthousand.
- AUC scores and ROC curve looked promising in 4-5 smpl:thousand, but this is most likely down to low number of epochs, not evaluating set fully.

### Approach 2:
- Less Layers and less units to overcome overfitting in Approach 1.
- Loss functions look good, still accuracy showing signs of overfitting.
- Poor AUC score.
- See 2.1.1
- **Higher dropout rates**:
  - Changed dropout rates 0.2 - 0.5.
  - Smaller batch size
- Dropout 0.5 gave high fluctuating AUC results for different runs (0.42 - 0.68), with high val and training acc as before.
- Best results with (BS=64, DR=0.5, units=8-16, layers=2)
- (BS=64, DR=0.5, units=4, layers=4) gives more consistent AUC values. Validation loss low and acc high whilst training loss high, and accuracy around 0.7. Not as good but more realistic see 2.2.2
- (BS=64, DR=0.5, units=8, layers=4) better acc and loss value with same consistent AUC scores, see 2.2.3.
- "" "" with units=16 showing promising, very sporadic though
- (BS=64, **DR=0.4**, units=4, layers=4) more consistent loss and accuracy, see 2.2.4.
