Imports System.Collections.Specialized

Namespace Helpers
    Public Class BinaryBaqHelper
        Private itemIdBitSector As BitVector32.Section = BitVector32.CreateSection(63)
        Private value1BitSector As BitVector32.Section = BitVector32.CreateSection(15, itemIdBitSector)
        Private value2BitSector As BitVector32.Section = BitVector32.CreateSection(15, value1BitSector)
        Private value3BitSector As BitVector32.Section = BitVector32.CreateSection(15, value2BitSector)
        Private value4BitSector As BitVector32.Section = BitVector32.CreateSection(15, value3BitSector)
        Private value5BitSector As BitVector32.Section = BitVector32.CreateSection(15, value4BitSector)

        Private Const BitVectorByteSize As Integer = 4
        Private Const NumberOfBytes As Integer = 8 'Defined in old CSO version as the number of bytes reserved for one item

#Region " Constructors "
        ''' <summary>
        ''' Instantiate a new BinaryBaqHelper
        ''' </summary>
        ''' <param name="baqAnswers"></param>
        ''' <param name="itemIndex">config index - 1 / 5</param>
        ''' <remarks>
        ''' The baqAnswers byteArray consists of 480 bytes. This byteArray holds 60 items of each 8 bytes.
        ''' The 8 bytes are divided into two bitvectors of 32 bits. The first bitvector holds the normative values for the five statements.
        ''' The second bitvector holds the ipsative values.
        ''' Both the normative and ipsative bitvector is devided in the following sections:
        '''  - 6 bits for the itemd id
        '''  - 4 bits for the value of the first value
        '''  - 4 bits for the value of the second value
        '''  - 4 bits for the value of the third value
        '''  - 4 bits for the value of the fourth value
        '''  - 4 bits for the value of the fifth value
        ''' </remarks>
        Public Sub New(baqAnswers As Byte(), itemIndex As Integer, numberOfStatements As Integer)
            Dim offSet As Integer = 0
            Dim itemBytes(NumberOfBytes - 1) As Byte

            'Get the bytes for the question index
            offSet = CInt((itemIndex - 1) / numberOfStatements) * NumberOfBytes
            For byteIndex As Integer = 0 To NumberOfBytes - 1 'Get the bytes for one item
                itemBytes(byteIndex) = baqAnswers(offSet + byteIndex)
            Next

            Dim normative As Integer = System.BitConverter.ToInt32(itemBytes, 0)
            Dim ipsative As Integer = System.BitConverter.ToInt32(itemBytes, BitVectorByteSize)

            Dim normativeBitVector As New BitVector32(normative)
            Dim ipsativeBitVector As New BitVector32(ipsative)

            _ItemId = normativeBitVector(itemIdBitSector)
            _NormativeValues.Add(normativeBitVector(value1BitSector))
            _NormativeValues.Add(normativeBitVector(value2BitSector))
            _NormativeValues.Add(normativeBitVector(value3BitSector))
            _NormativeValues.Add(normativeBitVector(value4BitSector))
            _NormativeValues.Add(normativeBitVector(value5BitSector))

            _IpsativeValues.Add(ipsativeBitVector(value1BitSector))
            _IpsativeValues.Add(ipsativeBitVector(value2BitSector))
            _IpsativeValues.Add(ipsativeBitVector(value3BitSector))
            _IpsativeValues.Add(ipsativeBitVector(value4BitSector))
            _IpsativeValues.Add(ipsativeBitVector(value5BitSector))
        End Sub
#End Region

#Region " Properties "
        Public Property ItemId As Integer
        Public Property NormativeValues As New List(Of Integer)
        Public Property IpsativeValues As New List(Of Integer)
#End Region

#Region " Methods "
        ''' <summary>
        ''' Update answersbinary on item index
        ''' </summary>
        ''' <param name="answersBytes"></param>
        ''' <param name="itemIndex"></param>
        ''' <remarks>
        ''' The baqAnswers byteArray consists of 480 bytes. This byteArray holds 60 items of each 8 bytes.
        ''' The 8 bytes are divided into two bitvectors of 32 bits. The first bitvector holds the normative values for the five statements.
        ''' The second bitvector holds the ipsative values.
        ''' Both the normative and ipsative bitvector is devided in the following sections:
        '''  - 6 bits for the itemd id
        '''  - 4 bits for the value of the first value
        '''  - 4 bits for the value of the second value
        '''  - 4 bits for the value of the third value
        '''  - 4 bits for the value of the fourth value
        '''  - 4 bits for the value of the fifth value
        ''' </remarks>
        Public Sub PutBinary(ByRef answersBytes As Byte(), itemIndex As Integer, numberOfStatements As Integer)
            Dim offSet As Integer = 0
            Dim itemBytes(NumberOfBytes - 1) As Byte '8 bytes

            'Get the bytes for the question index
            offSet = CInt((itemIndex - 1) / numberOfStatements) * NumberOfBytes

            Dim normativeBitVector As New BitVector32(0)
            normativeBitVector(itemIdBitSector) = _ItemId
            normativeBitVector(value1BitSector) = _NormativeValues(0)
            normativeBitVector(value2BitSector) = _NormativeValues(1)
            normativeBitVector(value3BitSector) = _NormativeValues(2)
            normativeBitVector(value4BitSector) = _NormativeValues(3)
            normativeBitVector(value5BitSector) = If(_NormativeValues.Count > 4, _NormativeValues(4), 0)

            Dim ipsativeBitVector As New BitVector32(0)
            ipsativeBitVector(itemIdBitSector) = _ItemId
            ipsativeBitVector(value1BitSector) = _IpsativeValues(0)
            ipsativeBitVector(value2BitSector) = _IpsativeValues(1)
            ipsativeBitVector(value3BitSector) = _IpsativeValues(2)
            ipsativeBitVector(value4BitSector) = _IpsativeValues(3)
            ipsativeBitVector(value5BitSector) = If(_IpsativeValues.Count > 4, _IpsativeValues(4), 0)

            Dim normativeBytes As Byte() = System.BitConverter.GetBytes(normativeBitVector.Data)
            Dim ipsativeBytes As Byte() = System.BitConverter.GetBytes(ipsativeBitVector.Data)

            For i As Integer = 0 To BitVectorByteSize - 1
                itemBytes(i) = normativeBytes(i)
                itemBytes(BitVectorByteSize + i) = ipsativeBytes(i)
            Next

            'Update the bytes for the question index
            For byteIndex As Integer = 0 To NumberOfBytes - 1
                answersBytes(offSet + byteIndex) = itemBytes(byteIndex)
            Next
        End Sub
#End Region

    End Class
End Namespace