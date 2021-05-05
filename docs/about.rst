.. _about:

==================
About ``covid-ht``
==================

Blood Measurement (*hemogram*) is a common practice among Health Professionals as part of the toolkit to diagnose and evaluate a wide variety of health conditions.

While some of the measurements can characterize certain conditions, others provide information about "general functioning" which may reflect the ongoing of conditions.

Diagnosis and evaluation of conditions which take into account hemograms is done by Health Professionals based on individual knowledge and experience.

While there are specific blood measurements for COVID19, those haven't been widely available in many places - i.e. Perú - having to resort to other tools for the diagnosis, i.e. x-rays, tomographies, non-specific Blood Measurements, etc.

Non-specific Blood Measurements - i.e. Complete Blood Counts - are widely available, affordable and already incorporated into the Health Professional practice.

A "general guide" is commonly provided in the results with reference values in order to help "classify" the patient (i.e. healthy or non-healthy).

Departure from those reference values may indicate an ongoing condition - i.e. bacterial or viral infection - which, with the assement of symptoms (and perhaps other diagnosis tools) leads to the diagnosis and therefore treatment.

While there are guidelines to detect an infection through hemogram results, the specific effects on hemograms of COVID19 are being studied, i.e. in `C-reactive protein`_ and `viscosity`_.

*Independently of the causes of such effects, as long as those are consistent to a "considerable" part of the population, a classifier can be developed in order to improve the toolkit of Health Professionals.*

This project aims to provide a tool to efficiently build and manage that classifier and make it effectively available for widespread use in order to improve detection, evaluation and resource efficiency of the COVID19 pandemic.

Early detection is deemed to be the greatest success factor in COVID19 treatments.

Improvements in early detection should increase successful treatments, potentially saving lives.

Improved evaluation and resource efficiency can also be achieved with the tool, i.e. by only using expensive specific COVID19 testing for assesing full recovery when the classification of the hemogram indicates so.

`A machine-learning classifier can outperform top-level Human experts' classification`_. AI classifiers takes into account relations and differences that are hard to spot to most Humans systematically.

If this classifier achieves an adequate accuracy through hemograms and is made publicly available, all Health Professionals with a smart-phone and Internet access could classify any hemogram with the same accuracy as top-level experts on the matter, improving the information available from the measurement for the case with little to no infrastructure modifications.

`This tool is totally transparent <https://github.com/math-a3k/covid-ht>`_ - based on Free and Open Source Software and Open Standards at all levels of its stack - and suitable for Reproducible Research. You may audit it entirely to fully understand how it works, what it provides and its limitations. It is distributed under the GNU LGPLv3 license.

The tool is not a replacement of Health Professionals.

Any diagnostic and treatment should be decided by a Health Professional with the patient. If you are an individual with a recent hemogram result, the tool may indicate to take preemptive care and seek a Health Professional.

Also, don't blame the knife providers: This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Is something not working correctly? Could something be done better? Any questions? Everybody is welcome to join the community for building and using it:

* covid-ht+subscribe@googlegroups.com
* https://github.com/math-a3k/covid-ht

.. _C-reactive protein: https://onlinelibrary.wiley.com/doi/10.1111/bjh.17306
.. _viscosity: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8010604/
.. _A machine-learning classifier can outperform top-level Human experts' classification: https://www.theguardian.com/society/2020/jan/01/ai-system-outperforms-experts-in-spotting-breast-cancer
