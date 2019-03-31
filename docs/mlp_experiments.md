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

- **(BS=64, DR=0.5, units=8, layers=4):**
  - Training: 65000, Validation: 6000, Test: 2000
  - Better acc and loss value with same consistent AUC scores, see 2.2.3.
  - Performed well on validation but test set gave very high values for loss, albeit some promising accuracy scores. see *2.2.3*.
  - Notes:
    - Fixed a bit of overfitting but test data still suggests huge overfitting, which is reflected by loss data.
    -


- **(BS=64, DR=0.4, units=4, layers=4):**
  - more consistent loss and accuracy, see *2.2.4*.
  - Training accuracy much lower, validation accuracy lower. Training loss high but lower loss in test. And respectable accuracy scores. AUC shite but hey.
  - Dropout seems to be causing divergence in training and Validation accuracy and loss, going to test lowering it.

  - *Drops Dropout to 0.25*
  - Led to much higher training acc.
  - Same test scores

**Upped training:75000, validation: 10000, test: 4000**

- **(BS=128, DR=0.25, units=4, layers=3):**
  - Consistent train/val loss/acc.
  - Test loss Not looking tooo hot.

- **(BS=128, DR=0.25, units=8, layers=3):**
    - Consistent train/val loss/acc.
    - Test loss highhhh

- **(BS=128, DR=0.25, units=16/32, layers=3):**
    - Consistent train/val loss/acc.
    - Test loss vvvvvv highhhh

    *More units seem to equal more overfitting*

- **(BS=128, DR=0.25, units=8, layers=5):**
    - Complex structure led to overfitting and quick convergence on training loss and accuracy, good auc scores.
    - High loss but good accuracy in test, same as always, see *2.2.5*

- *Trying simpler architecture to underfit*

- **(BS=128, DR=0.25, units=2, layers=6):**
    - Training loss doesn't drop, not complex enough.

- NGramm conclusion: All models defined in one way or another overfitted training data. More complex models tended to overfit it more severely. High accuracy levels were given by most architecture types but loss was high in all as well. ROC cureve didn't really tell much of a story. 2.2.3, 2.2.4 showed most promising performance.

- *upped NGRam range to 3







- "" "" with units=16 showing promising, very sporadic though
