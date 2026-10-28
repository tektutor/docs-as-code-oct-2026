Directives
==========

.. note::

   The BMS stores the last 100 faults.

.. warning::
   
   Never open the pack whilte it is charging.

.. code-block:: c
   :number-lines:

   if (cell_mv > MAX_CELL_MV) {
      open_contactor();
   }