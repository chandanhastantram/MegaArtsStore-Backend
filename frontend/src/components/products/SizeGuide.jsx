import Modal from '../common/Modal'
import './SizeGuide.css'

export default function SizeGuide({ isOpen, onClose, category = 'bangles' }) {
  const sizeCharts = {
    bangles: {
      title: 'Bangle Size Guide',
      description: 'Measure your wrist circumference to find your perfect bangle size.',
      measurements: [
        { size: '2.2', circumference: '5.5"', diameter: '55mm' },
        { size: '2.4', circumference: '6.0"', diameter: '60mm' },
        { size: '2.6', circumference: '6.5"', diameter: '65mm' },
        { size: '2.8', circumference: '7.0"', diameter: '70mm' },
        { size: '2.10', circumference: '7.5"', diameter: '75mm' },
        { size: '2.12', circumference: '8.0"', diameter: '80mm' }
      ],
      instructions: [
        'Use a flexible measuring tape',
        'Wrap it around the widest part of your hand (knuckles)',
        'Keep the tape snug but not tight',
        'Note the measurement in inches'
      ]
    },
    rings: {
      title: 'Ring Size Guide',
      description: 'Measure your finger circumference to find your ring size.',
      measurements: [
        { size: '5', circumference: '1.94"', diameter: '15.7mm' },
        { size: '6', circumference: '2.04"', diameter: '16.5mm' },
        { size: '7', circumference: '2.14"', diameter: '17.3mm' },
        { size: '8', circumference: '2.24"', diameter: '18.1mm' },
        { size: '9', circumference: '2.34"', diameter: '18.9mm' },
        { size: '10', circumference: '2.44"', diameter: '19.8mm' }
      ],
      instructions: [
        'Use string or paper strip',
        'Wrap around finger base',
        'Mark where ends meet',
        'Measure the length'
      ]
    },
    necklaces: {
      title: 'Necklace Length Guide',
      description: 'Choose your necklace length based on your preferred style.',
      measurements: [
        { size: 'Choker', circumference: '14-16"', diameter: 'Sits close to neck' },
        { size: 'Princess', circumference: '17-19"', diameter: 'Sits at collarbone' },
        { size: 'Matinee', circumference: '20-24"', diameter: 'Sits at bust line' },
        { size: 'Opera', circumference: '28-36"', diameter: 'Sits at waist' },
        { size: 'Rope', circumference: '36"+', diameter: 'Can be doubled' }
      ],
      instructions: [
        'Consider your neckline',
        'Shorter lengths for smaller frames',
        'Longer lengths for layering',
        'Measure existing necklaces as reference'
      ]
    }
  }

  const chart = sizeCharts[category] || sizeCharts.bangles

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={chart.title} size="medium">
      <div className="size-guide">
        <p className="size-guide-description">{chart.description}</p>

        {/* Size Chart Table */}
        <div className="size-chart-table">
          <table>
            <thead>
              <tr>
                <th>Size</th>
                <th>Circumference</th>
                <th>Diameter</th>
              </tr>
            </thead>
            <tbody>
              {chart.measurements.map((item, index) => (
                <tr key={index}>
                  <td><strong>{item.size}</strong></td>
                  <td>{item.circumference}</td>
                  <td>{item.diameter}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Measurement Instructions */}
        <div className="measurement-instructions">
          <h4>How to Measure</h4>
          <ol>
            {chart.instructions.map((instruction, index) => (
              <li key={index}>{instruction}</li>
            ))}
          </ol>
        </div>

        {/* Visual Guide */}
        <div className="visual-guide">
          <div className="guide-icon">📏</div>
          <p>
            <strong>Pro Tip:</strong> Measure at the end of the day when your hands are 
            slightly larger. If between sizes, choose the larger size for comfort.
          </p>
        </div>
      </div>
    </Modal>
  )
}
